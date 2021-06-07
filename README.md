# MA_2021

Python3 needs to be installed. To get scripts working, do the following steps:

1. pip3 install -r requirements.txt
2. python3 preprocessing_a.py "Path/CSV_name.csv"
3. python3 prototype_a.py (current version: adjust the function you want to use directly in the script in the main function.)
    
    -> you will be asked which file you want to analyze after starting the script

4. Upload in neo4j database: Make sure to place the CSV file in the import folder of your neo4j installation. After starting the server, you can use the statements provided in the "Neo4j Import" file (you have to adjust the file name). 

    -> NOTE: Make sure there are no special characters such as: Ää Öö Üü ß "" '' (also check column names). Otherwise there will be an error  like "Cannot merge the following node because of null property value for ..."

5. Example cypher queries are provided in "Example Queries" and can be adjusted to your needs
