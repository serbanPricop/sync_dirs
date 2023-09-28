import os
import hashlib
import time

LOG = 'log.txt'


# function area
# -------------------------------------------------------------

# log function
def log(message):
    # write log
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG, 'a') as f:
        f.write('['+now+']'+message+'\n')

def convert_to_seconds(minutes_interval):
    # convert minutes to seconds
    return int(minutes_interval) * 60


def compare_file(file_one, file_two):
    # compare 2 files with hash
    with open(file_one, 'rb') as f1:
        with open(file_two, 'rb') as f2:
            if hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest():
                return True
            else:
                return False

def compare_hash_folder(root_folder, replica):
    # compare hash folder
    # return True if all file is same
    # return False if any file is different
     # get all file in folder
    root_files = os.listdir(root_folder)
    # get all file in backup
    replica_files = os.listdir(replica)
    # compare 2 list
    if len(root_files) != len(replica_files):
        return False

    for file in root_files:
        if file in replica_files:
            if not compare_file(root_folder+'/'+file, replica+'/'+file):
                return False
        else:
            return False
    return True

#------------------------------------------------------------------
log('Start')

if os.path.isfile('config.txt'):
    print("config file: OK")
    log ('config file: OK')
    # get variable from config
    with open('config.txt', 'r') as f:
        lines = f.readlines()
        root_dir = lines[0].split(':')[1].strip()
        replica_dir = lines[1].split(':')[1].strip()

else:
    log('config file: NOT FOUND')
    print("config file: NOT FOUND")
    # register dirs
    root_dir = input('Root dir path:')
    replica_dir = input('Replica dir path:')
    time_interval = input('Please specify time interval(minutes):')
    # check if root is exist
    if not os.path.isdir(root_dir):
        log('root: NOT FOUND')
        print('Root folder does not exist')
        exit()
    # check if replica is exist
    if not os.path.isdir(replica_dir):
        log('replica: NOT FOUND')
        print('Replica folder does not exist')
        exit()
    # write config
    with open('config.txt', 'w') as f:
        f.write('root:'+root_dir)
        f.write('\n')
        f.write('replica:'+replica_dir)
    print('config file: CREATED')
    log('config file: CREATED')

# run loop every 5 minutes

while True:
    # check if folder is same with backup
    if compare_hash_folder(root_dir, replica_dir):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{now}] file is up to date')
        log('file is up to date')
        # sleep for 5 minutes
        time.sleep(convert_to_seconds(time_interval))
        continue    

    # check root
    if os.path.isdir(root_dir):
        print('root: FOUND')
        log('root: FOUND')
    else:
        print('folder is not exist')
        log('folder is not exist')
        print('please check your config file')
        break

    # check replica
    if os.path.isdir(replica_dir):
        print('replica: FOUND')
        log('replica: FOUND')
    else:
        print('Replica dir does not exist')
        log('Replica dir does not exist')
        print('Please check your config file')
        break

    # check file hash in root and compare with replica
    countSync = 0
    updateFile = 0
    deleteFile = 0

    # get all file in folder
    files = os.listdir(root_dir)
    # get all file in backup
    files_backup = os.listdir(replica_dir)
    # compare 2 list
    for file in files_backup:
        if file in files:
            if compare_file(root_dir+'/'+file, replica_dir+'/'+file):
                log(f'{file} is up to date')
                countSync += 1
            else:
                # copy file from folder to backup
                updateFile += 1
                os.remove(replica_dir+'/'+file)
                os.system('cp '+root_dir+'/'+file+' '+replica_dir)
                log(f'{file} is updated')
        if file not in files:
            # delete file in backup
            log(f'{file} is deleted')
            deleteFile += 1
            os.remove(replica_dir+'/'+file)

    for file in files:
        if file not in files_backup:
            # copy file from folder to backup
            updateFile += 1
            log(f'{file} is copied')
            os.system('cp '+root_dir+'/'+file+' '+replica_dir)



    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'[{now}] sync: {countSync}; update: {updateFile}; delete: {deleteFile};')

    # sleep for 5 minutes
    time.sleep(convert_to_seconds(time_interval))
