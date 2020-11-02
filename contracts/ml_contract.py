from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split


def f(o, shard_num):
    print("f called", shard_num)
    data = load_breast_cancer()
    X = data.data
    Y = data.target
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.1, random_state=10)
    print("data loaded and split")
    if shard_num == 0:
        from sklearn import svm
        clf = svm.SVC()
        print("fit started")
        clf.fit(X_train, Y_train)
        accuracy = clf.score(X_test, Y_test)
        predictions = list(clf.predict(X_test))
        print("returning")
        return "SVC:" + " ----accuracy:" + str(accuracy) + " ------predictions:" + str(predictions)
    elif shard_num == 1:
        from sklearn import tree
        clf = tree.DecisionTreeClassifier()
        print("fit started")
        clf.fit(X_train, Y_train)
        accuracy = clf.score(X_test, Y_test)
        predictions = list(clf.predict(X_test))
        print("returning")
        return "DecisionTree:" + " ------accuracy:" + str(accuracy) + " -----predictions:" + str(predictions)
    return None
