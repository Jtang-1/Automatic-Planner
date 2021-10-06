from Test import Test
from Test import Test2
import jsonpickle

def run():
    #pprint(places_api.get_place_id("mcdonald"))
    #pprint(places_api.get_place_id("starbucks"))
    #pprint(dist_mtrx_api.distance_dict(["mcdonald","popeye","UCI"], ["starbucks","Great Park"]))
    new_test2 = Test2("Dabdub", "CS")
    new_test = Test(new_test2, "A")
    print("print1", new_test.get_students())
    serialized_test = new_test.to_json()
    print("print2", serialized_test)
    print("type", type(serialized_test))

    new_test3 = jsonpickle.decode(serialized_test)
    print("print3", type(new_test3.get_students()[0].get_subjects()))
    print("print4", type(new_test3))
    print("print5", new_test3.get_students())
    new_test3.add_student("Alpine")
    print(new_test3.get_students())

    new_dict = {}
    new_dict[new_test2] = 3
    for x in new_dict:
        print(x)



if __name__ == '__main__':
    run()

