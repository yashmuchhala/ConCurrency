from pprint import pprint
import jsonpickle


class Logger():
    @staticmethod
    def pubnub_log(message):
        print("----------------------")
        print("New message received:")
        print(message.__dict__)
        print("----------------------")

    @staticmethod
    def publish_attempt(o):
        print("----------------------")
        print("Attempting to publish " + str(type(o)))
        print(o.__dict__)
        print("----------------------")

    @staticmethod
    def succesfull_publish(result, status):
        print("----------------------")
        if status.error:
            print(jsonpickle.encode(result), jsonpickle.encode(status))
        else:
            print("Successfully published")
        print("----------------------")

    @staticmethod
    def p(s):
        print(s)
