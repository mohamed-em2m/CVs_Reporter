def extra_preprocessing(df):
    df["University"]=df["University"].apply(lambda x:x.lower())
    df["University"]=df["University"].apply(lambda x:"japan University" if "japan" in x else x)
    df["Department"]=df["Department"].apply(lambda x:"AI Department" if "ai" in x.lower() else x)
    df["Department"]=df["Department"].apply(lambda x:"AI Department" if "machine learning" in x.lower() else x)
    df["College"]=df["College"].apply(lambda x: "Computer Science" if "Artificial Intelligence" in x else x)
    df["College"]=df["College"].apply(lambda x: "Engineering" if "df Science" in x else x)
    