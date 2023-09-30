import sys, os, time, logging, schedule

def copy_file(source_file, destination_file):
    """
    Copy a file
    Input: 
    source_file: The source path of the file to be copied 
    destination_file: The destination path to where the source file will be copied
    Output: The file from the source path is copied in the destination path
    """
    
    try:
        with open(source_file, 'r') as source, open(destination_file, 'w') as destination:
            destination.write(source.read())

    except FileNotFoundError:
        print("File " + source_file+ " not found.")
        logging.info("File " + source_file+ " not found.")

    except Exception as e:
        print("An error occurred: "+e)
        logging.info("An error occurred: "+e)

def remove_tree(directory):
    """
    Removes the tree of a directory
    Input: 
    directory: The path to the directory tree to be removed
    Output: The directory tree is removed
    """

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        if os.path.isfile(item_path):
            os.remove(item_path)
            logging.info("Deleting file called: "+item_path)
            print("Deleting file called: "+item_path)
        elif os.path.isdir(item_path):
            remove_tree(item_path)

    os.rmdir(directory)
    logging.info("Deleting directory called:"+directory)
    print("Deleting directory called:"+directory)

def delete_directories(source_directory, destination_directory):
    """
    Deleting directory that do not exist in the source directory but exist in destination directory from the destination directory
    Input: 
    source_directory: The path of the source directory 
    destination_directory: The path of the destination directory
    Output: Files, directories or any directory trees from the destination directory that do not exist in the source directory are deleted
    """

    if os.path.isdir(source_directory):
        source_items = set(os.listdir(source_directory))
        destination_items = set(os.listdir(destination_directory))          
        items_to_delete = destination_items - source_items

        if len(items_to_delete)==0:
            for item in destination_items:
                source_item = os.path.join(source_directory, item)
                destination_item = os.path.join(destination_directory, item)
                synchronize_directories(source_item, destination_item)

        for item in items_to_delete:
                item_path = os.path.join(destination_directory, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    logging.info("Deleting file called: "+item_path)
                    print("Deleting file called: "+item_path)
                elif os.path.isdir(item_path):
                    remove_tree(item_path)

def synchronize_directories(source_directory, destination_directory):
    """
    Synchronizes the destination directory to reflect the source directory
    Input: 
    source_directory: The path of the source directory 
    destination_directory: The path of the destination directory
    Output: The items (files/directories/directory trees) from the destination path are synchronized with the ones from the source path
    """

    # If destination directory does not exist, create it
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        logging.info("Creating destination directory called: "+destination_directory)
        print("Creating destination directory called: "+destination_directory)

    # Iterate through all of the items in the source directory in order to copy them to the source directory
    if os.path.isdir(source_directory):
        for item in os.listdir(source_directory):
            source_item = os.path.join(source_directory, item)
            destination_item = os.path.join(destination_directory, item)

            # If the destination item (file or directory) does not exist, copy it
            if not os.path.exists(destination_item):
                if os.path.isfile(source_item):
                    copy_file(source_item, destination_item)
                    logging.info("Copying file called: "+destination_item)
                    print("Copying file called: "+destination_item)

                elif os.path.isdir(source_item):
                    synchronize_directories(source_item, destination_item)
                    logging.info("Copying directory called: "+destination_item)
                    print("Copying directory called: "+destination_item)

            # If it exists, then it might me just the file contents were modified
            else:
                if os.path.isfile(source_item):
                    with open(source_item, 'r') as file1, open(destination_item, 'r') as file2:
                        content1 = file1.read()
                        content2 = file2.read()
                    # Compare the contents of the files
                    if content1 != content2:
                        copy_file(source_item, destination_item)
                        logging.info("Copying file contents for: "+destination_item)
                        print("Copying file contents for: "+destination_item)

    # Delete any potentially missing files/directories/directory trees
    delete_directories(source_directory, destination_directory)

def main(source_directory, destination_directory, time_interval_seconds, log_path):
    """
    The main function in which we will schedule a job to be executed as often as we need it to
    I have chosen to synchronize the files once every couple of seconds but it can be adapted depending on our needs 
    to minutes, hours or even scheduled at a certain time every day thanks to the schedule library
    Input:
    source_directory: The path to the source directory that we use for synchronization
    destination_directory: The path in which the source directory is synchronized
    time_interval_seconds: The time interval (now in seconds) that we want our files to be synchronized
    log_path: The path to where we will be able to find all of the logs for creation/copying/removal operations
    Output: When it is scheduled, the job (in our case synchronize_directories) will be run and so our files will be synchronized
    """
    # Create a log for the create/copy/delete operations
    logger = logging.basicConfig(filename=log_path, level=logging.INFO,
                    format="%(asctime)s %(message)s", filemode="a")
    
    # Create a schedule that will run directories synchronization function every 'time_interval_seconds' seconds
    schedule.every(time_interval_seconds).seconds.do(synchronize_directories, source_directory, destination_directory)

    # Create an infite loop that will run the pending scheduled task
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])