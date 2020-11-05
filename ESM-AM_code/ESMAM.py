from algorithm import ESMAM
import argparse
import re
import glob
from datetime import datetime


if __name__ == '__main__':
       
    # parse args setting
    parser = argparse.ArgumentParser(description='Exceptional Survival Model Ant-Miner algorithm')
    
    group_paths = parser.add_mutually_exclusive_group(required=True)
    group_paths.add_argument("--p", type=str,
                             help="Dataset File path")
    group_paths.add_argument("--fd", type=str,
                             help="Dataset Folder path: runs ESM-AM on all .csv files in folder")
    
    parser.add_argument("--s", type=str,
                        help="Path to save log-results")
    parser.add_argument("--dtype", action="store_true",
                        help="Use _dtypes.json file")
    parser.add_argument("--n", type=str, default='esmam',
                        help="Name prefix for log-files")
    
    parser.add_argument("--ants", type=int, default=3000,
                        help="Number of ants")
    parser.add_argument("--minCases", type=int, default=10,
                        help="Minimum number of cases per rule")
    parser.add_argument("--maxUncover", type=int, default=0,
                        help="Maximum number of remaining uncovered cases")
    parser.add_argument("--converg", type=int, default=10,
                        help="Number of identical rules to convergence")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Level of significance of the Logrank test")
    parser.add_argument("--featTime", type=str, default='survival_time',
                        help="Survival Time feature name")
    parser.add_argument("--featEvent", type=str, default='survival_status',
                        help="Survival Status feature name")
    
    args = parser.parse_args()
    path = args.p
    folder = args.fd
    save_path = args.s
    dtypes = args.dtype
    prefix = args.n
    
    no_of_ants = args.ants
    min_cases_per_rule = args.minCases
    max_uncovered_cases = args.maxUncover
    no_rules_converg = args.converg
    alpha = args.alpha
    t_feat = args.featTime
    e_feat = args.featEvent
    
    
    # FILE EXECUTION
    if path:
        print('> running file {} ({})'.format(path, datetime.now()))
        if dtypes:
            dtype_file = path.split('.')[0] + '_dtypes.json'
        else: dtype_file = None
        
        if save_path: name_prefix = save_path + '/' + prefix
        
        # ESM-AM run    
        alg = ESMAM(no_of_ants, min_cases_per_rule, max_uncovered_cases, no_rules_converg, alpha)
        alg.read_data(path, dtype_file, t_feat, e_feat)
        alg.fit()    
        alg.save_results(name_prefix)
    
    # FOLDER EXECUTION
    else:
        print('Processing folder: {}'.format(folder))
        
        for file in glob.iglob(folder + '/*.csv'):
           print('> running file {} ({})'.format(file, datetime.now())) 
           
           prefix = re.split(r'(\\)|(\/)',file)[-1].split('.')[0]
           if save_path: name_prefix = save_path + '/' + prefix
           
           if dtypes:
               dtype_file = file.split('.')[0] + '_dtypes.json'
           else: dtype_file = None
           
           # ESM-AM run    
           alg = ESMAM(no_of_ants, min_cases_per_rule, max_uncovered_cases, no_rules_converg, alpha)
           alg.read_data(file, dtype_file, t_feat, e_feat)
           alg.fit()    
           alg.save_results(name_prefix)