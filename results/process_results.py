'''CODE FOR PROCESSING ESM-AM LOG FILES'''
import pandas as pd
import numpy as np
import concurrent.futures
import multiprocessing
import matplotlib.backends.backend_pdf
import glob
import math
import argparse
import re
import json
from itertools import chain
from datetime import datetime
from lifelines import KaplanMeierFitter
from matplotlib import pyplot as plt
from matplotlib.pylab import rcParams


def survival_plots(SAVE_PATH, KM_FILE_NAME, rules, lifelinesModels):
    # generate pdf with survival model (all rules) and each rule (vs cmp and pop)
    print('> generating plots')
    
    def get_RuleString(rule_id, rule_dict):
        return '{}: '.format(rule_id) + ' and '.join(['<{}={}>'.format(str(attr), str(val).replace('.0','')) for (attr,val) in rule_dict.items()])
    
    pdf = matplotlib.backends.backend_pdf.PdfPages(SAVE_PATH) # .pdf file 
    
    # Final rule-model figure
    rcParams.update({'font.size': 14})
    rcParams['figure.figsize'] = 15, 10

    plt.figure(num='ruleModel')
    ax = plt.subplot(111)
    
    kmModels = pd.read_csv(KM_FILE_NAME,header=0)
    x = kmModels.times.values
    columns = list(kmModels.columns)
    columns.remove('times')
    for column in columns:
        if column == "population":
            ax.plot(x, kmModels[column], color='k', label='{}'.format(column), linestyle=':')
        else:
            ax.plot(x, kmModels[column], label='{}'.format(column))

    plt.title('Rule-Set (subgroups) Survival Models')
    plt.tight_layout(pad=1.25)
    plt.xlabel('Time')
    plt.xlim(0, x[-1]+3)
    plt.xticks([])
    plt.ylabel('Survival probability')
    plt.yticks([0,0.2,0.4,0.6,0.8,1])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.legend(frameon=False, bbox_to_anchor=(1.01, 1), loc=2)
    pdf.savefig(plt.figure(num='ruleModel'), bbox_inches='tight')
    plt.close(fig='ruleModel')
    
    # Individual rules
    n_rows = math.ceil(len(rules)/2)
    rcParams['figure.figsize'] = 15, 3*n_rows
    rcParams['axes.titlesize'] = 11
    
    #plt.figure(num='indiv_rules')
    fig, axes = plt.subplots(nrows=n_rows, ncols=2, sharex=True, sharey=True, num='indiv_rules')
    ax_id = 0

    for rule_id in rules.keys():

        ax = axes.flatten()[ax_id]
        ax_id += 1
        
        lifelinesModels['population'].plot(ax=ax, ci_show=False, c='k', ls=':')
        lifelinesModels[rule_id]['sg'].plot(ax=ax, ci_show=False, c='firebrick')
        lifelinesModels[rule_id]['cmp'].plot(ax=ax, ci_show=False, c='tab:blue')
     
        ax.set_title(get_RuleString(rule_id, rules[rule_id]), loc='left')
        ax.set_xlabel('Time')
        ax.set_ylabel('Survival probability')
        ax.set_ylim([0, 1])
        ax.set_xlim([0, x[-1]+3])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(frameon=False, bbox_to_anchor=(1.01, 1), loc=2)
        plt.tight_layout(pad=1.25)
        plt.xticks([])
    
    for i in range(ax_id, 2*n_rows):
        fig.delaxes(axes.flatten()[i])
        
    pdf.savefig(plt.figure(num='indiv_rules'), bbox_inches='tight')
    plt.close(fig='indiv_rules')
    pdf.close()    
    return

def integratedBrierScore(rule_cases, dataset, ruleModels, T_FEAT, E_FEAT, **kwargs):
    # Computs IBS over a single rule
    
    # individual Brier Score
    def BS_i(t_i, e_i, t_Star, survFnc, censorFnc, col_time=0, col_fnc=1):
        # case Ti < T*, event=True
        if t_i <= t_Star and e_i == True:
            S_tStar = survFnc.loc[survFnc[survFnc.columns[col_time]] == t_Star, survFnc.columns[col_fnc]].iloc[0]
            G_Ti = censorFnc.loc[censorFnc[censorFnc.columns[col_time]] == t_i, censorFnc.columns[col_fnc]].iloc[0]
            return (0 - S_tStar) ** 2 / G_Ti
        # case Ti > T*
        elif t_i > t_Star:
            S_tStar = survFnc.loc[survFnc[survFnc.columns[col_time]] == t_Star, survFnc.columns[col_fnc]].iloc[0]
            G_tStar = censorFnc.loc[censorFnc[censorFnc.columns[col_time]] == t_Star, censorFnc.columns[col_fnc]].iloc[0]
            return (1 - S_tStar) ** 2 / G_tStar
        # case otherwise
        else:
            return 0
    
    sg_times = dataset[T_FEAT].iloc[rule_cases]
    sg_events = dataset[E_FEAT].iloc[rule_cases]
    sg_survfnc = ruleModels['sg'].survival_function_

    # variables
    times = sg_times.reset_index(drop=True)    # series
    events = sg_events.reset_index(drop=True)  # series
    survFnc = sg_survfnc.reset_index()         # df
    censorFnc = KaplanMeierFitter().fit(times, ~events, label='censorFnc').survival_function_.reset_index()  # df

    # constructs Brier Score matrix (observations x times)
    N = list(times.index)
    T = list(survFnc.iloc[:, 0])
    BSi = pd.DataFrame(index=N, columns=T)

    for time_star in T:  # use itertools
        for i in N:
            BSi.loc[i, time_star] = BS_i(times[i], events[i], time_star, survFnc, censorFnc)

    BSt = BSi.sum() / len(N)      # Brier Score over each time
    IBS = BSt.sum() / max(times)  # Integrated Brier Score (BS over all times)
    return IBS

def survivalModels(rules, covered_cases, db, T_FEAT, E_FEAT):
    
    cols = ['population'] + list(rules.keys())
    lifelinesModels = dict.fromkeys(cols)         # output: lifelinesModels = {population: KMFitter,
                                                  #                            rule_id : {sg: KMFitter, cmp: KMFitter}}

    # GENERATING KM MODELS
    lifelinesModels['population'] = KaplanMeierFitter()
    lifelinesModels['population'].fit(db[T_FEAT], db[E_FEAT], label='population')

    for rule_id in rules.keys():
        sg_index = covered_cases[rule_id]
        cmp_index = list(set(range(db.shape[0]))^set(sg_index))
        sg_times = db[T_FEAT].iloc[sg_index]
        cmp_times = db[T_FEAT].iloc[cmp_index]
        sg_event = db[E_FEAT].iloc[sg_index]
        cmp_event = db[E_FEAT].iloc[cmp_index]
        
        models = dict.fromkeys(['sg','cmp'])
        models['sg'] = KaplanMeierFitter()
        models['sg'].fit(sg_times, sg_event, label='{}'.format(rule_id))
        models['cmp'] = KaplanMeierFitter()
        models['cmp'].fit(cmp_times, cmp_event, label='{}-complement'.format(rule_id))
        lifelinesModels[rule_id] = models.copy()

    return lifelinesModels

def calc_IBS(rules, covered_cases, dataset, lifelinesModels, T_FEAT, E_FEAT, PARALEL, CPU):
    
    ibs = 0
    
    if PARALEL:
        print('> begin ibs ({}) #rules={} [paralel processing]'.format(datetime.now().strftime("%H:%M:%S"), len(rules)))
        args = [{'rule_cases':covered_cases[rule_id], 'dataset':dataset, 'ruleModels':lifelinesModels[rule_id], 'T_FEAT':T_FEAT, 'E_FEAT':E_FEAT} for rule_id in rules.keys()]
        with concurrent.futures.ProcessPoolExecutor(max_workers=CPU) as executor:
            results = [executor.submit(integratedBrierScore, **arg) for arg in args]
            for res in concurrent.futures.as_completed(results):
                ibs += res.result()
    
    else:
        print('> begin ibs ({}) #rules={} [sequential processing]'.format(datetime.now().strftime("%H:%M:%S"), len(rules)))
        for rule_id in rules:
            ibs += integratedBrierScore(covered_cases[rule_id], dataset, lifelinesModels[rule_id], T_FEAT, E_FEAT)
    print('ibs done ({})'.format(datetime.now().strftime("%H:%M:%S")))
    return ibs

def results(DB_PATH, RULE_FILE_NAME, T_FEAT, E_FEAT, PARALEL, CPU):
    
    metrics = {} # output
    
    # read _RuleSet.txt file into rules-dict
    temp = pd.read_table(RULE_FILE_NAME,header=None)
    db_rules = temp.drop(temp.head(2).index).reset_index(drop=True)[0]
    rules = {}
    for row in range(len(db_rules)):
        line = db_rules[row]
        r_idx,r = line.split(':')
        r = r.split('IF')[1].split('THAN')[0].replace(' ','')
        rule = {}
        for term in r.split('AND'):
            a,v = term.split('=')
            attr = a.replace('<','')
            value = v.replace('>','')
            if value == 'TUMORFREE':
                value = 'TUMOR FREE'
            if value == 'WITHTUMOR':
                value = 'WITH TUMOR'
            rule[attr] = value
        rules[r_idx] = rule.copy()

    # metrics: number of rules and average size
    size = 0
    for rule in rules.values():
        size += len(rule)
    metrics['num_rules'] = len(rules)
    metrics['length'] = size/len(rules)

    # metrics: comput covered cases and coverage
    db = pd.read_csv(DB_PATH, delimiter=',', header=0, index_col=False)
    covered_cases = {}
    for r in rules:
        db_temp = db.copy()
        for attr,value in rules[r].items():
            db_temp = db_temp[db_temp[attr].apply(str) == value]
        covered_cases[r] = list(db_temp.index)
    metrics['ruleCoverage'] = sum([len(item) for key,item in covered_cases.items()])/len(covered_cases)/db.shape[0]
    metrics['ruleCoverageSTD'] = np.std([len(item) for key,item in covered_cases.items()])/db.shape[0] 
    setCovered = list(set(chain(*covered_cases.values())))
    metrics['setCoverage'] = len(setCovered)/db.shape[0]
    
    # generates survival models from LifeLines Lib
    lifelinesModels = survivalModels(rules, covered_cases, db, T_FEAT, E_FEAT)
    
    # metrics: IBS
    metrics['IBS'] = calc_IBS(rules, covered_cases, db, lifelinesModels, T_FEAT, E_FEAT, PARALEL, CPU)
    
    return metrics, rules, lifelinesModels

def pipeline(_save_figs, _save_path, db_path, rule_file_name, km_file_name, T_FEAT, E_FEAT, PARALEL, CPU):
    
    metrics, rules, lifelinesModels = results(db_path, rule_file_name, T_FEAT, E_FEAT, PARALEL, CPU)
    if _save_figs:
        survival_plots(_save_path, km_file_name, rules, lifelinesModels)
    return metrics


if __name__ == '__main__':
    
    # parse args setting
    parser = argparse.ArgumentParser(description='Script to process the log files into results.')
    
    parser.add_argument("--p", type=str, required=True,
                        help="Log-files folder path")
    
    group_ex = parser.add_mutually_exclusive_group()
    group_ex.add_argument("--db", type=str,
                          help="Dataset .csv path (default uses --p)")
    group_ex.add_argument("--r", action="store_true",
                          help="Recurrent: process results in each (and all) subfolders")
    
    parser.add_argument("--noFigs", action="store_false",
                        help="Generates the survival models' plots in .pdf format")
    parser.add_argument("--parlel", action="store_true",
                        help="Paralel IBS computation: calculates IBS with paralel processing")
    parser.add_argument("--cpu", type=int, default=multiprocessing.cpu_count(),
                        help="Number of paralel cpus [default: os.cpu_count()]")
    parser.add_argument("--featTime", type=str, default='survival_time',
                        help="Survival Time feature name")
    parser.add_argument("--featEvent", type=str, default='survival_status',
                        help="Survival Status feature name")
    
    args = parser.parse_args()
    path = args.p
    db_path = args.db
    recurrent = args.r
    save_figs = args.noFigs
    paralel_proc = args.parlel
    n_cpu = args.cpu
    t_feat = args.featTime
    e_feat = args.featEvent
    
    
    # EXECUTION ON RECURSIVE SUBFOLDERS
    if recurrent:
        print('>> process recurrent folder: {}'.format(path))
        
        all_metrics = {}
        
        folders = [f for f in glob.iglob(path+'/*') if '.' not in f]
        for subfolder in folders:
            print('> subfolder: {}'.format(subfolder))
            
            rule_file_name = glob.glob(subfolder + '/*_RuleSet.txt')[0]
            km_file_name = glob.glob(subfolder + '/*_KM-Estimates.txt')[0]
            prefix = '_'.join(re.split(r'_', re.split(r'(\\)|(\/)',rule_file_name)[-1])[:-1])
            db_path = glob.glob(subfolder + '/*.csv')[0]
            save_path = path + '/{}_esmam-survivalModels.pdf'.format(prefix)
            
            all_metrics[prefix] = pipeline(save_figs, save_path, db_path, rule_file_name, km_file_name, t_feat, e_feat, paralel_proc, n_cpu)
        
        # save metrics
        with open(path+'/esmam_metrics.json', 'w') as f:
            json.dump(all_metrics, f)
    
    # SINGLE FOLDER RUN
    else:
        print('>> process single folder: {}'.format(path))
        rule_file_name = glob.glob(path + '/*_RuleSet.txt')[0]
        km_file_name = glob.glob(path + '/*_KM-Estimates.txt')[0]
        save_path = path + '/esmam_survivalModels.pdf'
        if not db_path:
            db_path = glob.glob(path + '/*.csv')[0]
        
        metrics = pipeline(save_figs, save_path, db_path, rule_file_name, km_file_name, t_feat, e_feat, paralel_proc, n_cpu)
        
        # save metrics
        with open(path+'/esmam_metrics.json', 'w') as f:
            json.dump(metrics,f, indent=2)
    

