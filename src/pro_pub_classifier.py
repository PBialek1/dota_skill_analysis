from matplotlib import pyplot as plt
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score


def f_importances(coef, names, title):
    imp = coef
    # imp = abs(imp)
    imp, names = (t for t in zip(*sorted(zip(imp.tolist()[0], names))))
    plt.barh(y=np.arange(len(names)), width=imp, align='center')
    plt.yticks(range(len(names)), names)
    plt.title(title)
    plt.tight_layout()
    plt.show()








def main():
    df = pd.read_pickle('data\\match_data.pkl')
    y = df['class']
    X = df.drop(labels='class', axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, test_size=.2)
    feature_names = X.columns.tolist()

    clf = svm.SVC(kernel='linear')
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(accuracy_score(y_test, y_pred))
    f_importances(clf.coef_, feature_names, 'SVM Model Weights')

    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(accuracy_score(y_test, y_pred))

    importances = clf.feature_importances_
    std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
    forest_importances = pd.Series(importances, index=feature_names)

    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    plt.show()
    # f_importances(clf.feature_importances_, feature_names, '')

    print('done')




if __name__ == '__main__':
    main()