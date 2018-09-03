# wikidata-historic-state-populations

*Estimated population for every US state between 1600-2018*

Uses a Wikidata SPARQL query (based off an example of national populations from
Wikidata) to grab known historic US state population data between 1600-2018.
Then, uses a Python script to *ROUGHLY* estimate population for every year
between known data points.

Intended to be used in combination with other kinds of historic data sets, such
as crime data for obtaining some kind of historical per-capita measurement.

---

[David J. Thomas](mailto:dave.a.base@gmail.com),
[thePortus.com](http://thePortus.com)<br />
Instructor of Ancient History and Digital Humanities,<br />
Department of History,<br />
[University of South Florida](https://github.com/usf-portal)

---

**To Use (Easiest)**

Either...
1. Use the raw results of the WikiData query from `1_wikidata_query_results.csv`, OR...
2. Use the complete estimated population results for every state and year from `2_wikidata_processed_results.csv`

**To Run**

1. Copy the query from the `data_files/1_query_wikidata.rq` file
2. Head to [Wikidata Query](query.wikidata.org), paste the query, run the query
3. Save the file in this directory
4. Run the python script in this directory `python 2_process_data.py -i INPUT_PATH -o OUTPUT_PATH` replacing INPUT_PATH with the name of your saved Wikidata results and OUTPUT_PATH with whatever you would like to save the file as
5. Use the saved results with full yearly population for your data needs
