class Configure:
    Azure_DB_CNString ='''Driver={ODBC Driver 13 for SQL Server};
                           Server=tcp:ellie-az-prd-01.database.windows.net,1433;
                           Database=Real_Estate;
                           Uid=SQLpython;
                           Pwd={Zw55227700};
                           Encrypt=yes;
                           TrustServerCertificate=no;
                           Connection Timeout=30;'''

    SQL_Server_DB_CNString = '''Driver={SQL Server};
                            Server=walkie-talkie\manteauDev;
                            Database=Properties;
                            Trusted_Connection=yes;'''
    min_price = 100000
    max_price = 30000000
    inc = 100000