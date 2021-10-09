import place_model.google_map_distance_matrix as dist_mtrx_api
from Test import Test
import jsonpickle
from place_model import google_map_places as places_api
import copy
import pprint


class Object1:
    def __init__ (self,att1):
        self.att1 = att1

    def test_print(self, words):
        print("wordword")


class Object2(Object1):
    def __init__(self, att1, att2):
        self.att2 = att2
        super().__init__(att1)

    def test_print2(self):
        print(self.att1)

def run():
    # print(places_api.get_place_id("mcdonald"))
    # print(places_api.get_place_id("starbucks"))
    # print(places_api.get_place_id("great park"))
    #print(dist_mtrx_api.distance_dict(["mcdonald","popeye","UCI"], ["starbucks","Great Park"]))
    # print(dist_mtrx_api.distance_dict("ChIJzUGCDNXc3IAR4l4UZu6QGLU", ["ChIJHZJ7UqHd3IARXzrKFEIBFyk","ChIJLw0j9C_d3IARMJuTL9e2Iyo"]))

    # test1 = Test("Student1", "grade1")
    # test2= Test("Student2", "grade2")
    # test3 = Test("Student3", "grade3")
    # test4 = Test("Student4", "grade4")
    # test5 = Test("Student5", "grade5")
    # test6 = Test("Student6", "grade6")
    #
    # test_dict = {test1: test2, test3: test4}
    #
    # e_test_dict = jsonpickle.encode(test_dict, keys="True")
    # d_test_dict = jsonpickle.decode(e_test_dict, keys="True")
    # print(test_dict)
    # print(d_test_dict)
    # if test_dict is d_test_dict:
    #     print("test dict before encoded = test dict after encode+decode")
    #
    # print(test1)
    # e_test1 = jsonpickle.encode(test1)
    # d_test1 = jsonpickle.decode(e_test1)
    # print(d_test1)
    # if test1 is d_test1:
    #     print("test object before encoded = test object after encode+decode")
    # a = {"a": 2, "b": 3}
    # b = {"a": 2, "b":3}
    # if a == b:
    #     print("True")
    #
    # e_num = jsonpickle.encode("pop")
    # d_num = jsonpickle.decode(e_num)
    # print(d_num)
    # if "pop" == d_num:
    #     print(True)
    #

    object2 = Object2("Jonathan", "Tang")
    print(object2)
    if isinstance(object2, Object1):
        print("is Object1")
    if isinstance(object2, Object2):
        print("is Object2")
    object2.test_print("wordword")
    object2.test_print2()




if __name__ == '__main__':
    run()

