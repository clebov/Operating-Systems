import threading

def sort(half_list, sorted_list):
    half_list.sort()
    sorted_list.extend(half_list)
    
def merge(left, right, whole_list):
    whole_list.extend(left)
    whole_list.extend(right)
    whole_list.sort()

if __name__ == "__main__":

    numbers = [234,34,23,3451,231,23,3423,2,3,4,23,23412,3]
    right_list = []
    left_list = []
    whole_list = []


    left = threading.Thread(target=sort(numbers[:(len(numbers)//2)], left_list))
    right = threading.Thread(target=sort(numbers[(len(numbers)//2):], right_list))
    complete_list = threading.Thread(target=merge(left_list, right_list, whole_list))

    left.start()
    left.join()
    print(left_list)

    right.start()
    right.join()
    print(right_list)

    complete_list.start()
    complete_list.join()
    print(whole_list)
    
    

