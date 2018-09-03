import os
import csv
import argparse

# setting constants
SCRIPT_NAME = os.path.basename(__file__)
FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
if not os.path.isabs(FOLDER_PATH):
    FOLDER_PATH = os.path.abspath(FOLDER_PATH)
STATE_NAMES = [
        ('Alabama', 'AL'),
        ('Alaska', 'AK'),
        ('Arizona', 'AZ'),
        ('Arkansas', 'AR'),
        ('California', 'CA'),
        ('Colorado', 'CO'),
        ('Connecticut', 'CT'),
        ('Delaware', 'DE'),
        ('Florida', 'FL'),
        ('Georgia', 'GA'),
        ('Hawaii', 'HI'),
        ('Idaho', 'ID'),
        ('Illinois', 'IL'),
        ('Indiana', 'IN'),
        ('Iowa', 'IA'),
        ('Kansas', 'KS'),
        ('Kentucky', 'KY'),
        ('Louisiana', 'LA'),
        ('Maine', 'ME'),
        ('Maryland', 'MD'),
        ('Massachusetts', 'MA'),
        ('Michigan', 'MI'),
        ('Minnesota', 'MN'),
        ('Mississippi', 'MS'),
        ('Missouri', 'MO'),
        ('Montana', 'MT'),
        ('Nebraska', 'NE'),
        ('Nevada', 'NV'),
        ('New Hampshire', 'NH'),
        ('New Jersey', 'NJ'),
        ('New Mexico', 'NM'),
        ('New York', 'NY'),
        ('North Carolina', 'NC'),
        ('North Dakota', 'ND'),
        ('Ohio', 'OH'),
        ('Oklahoma', 'OK'),
        ('Oregon', 'OR'),
        ('Pennsylvania', 'PA'),
        ('Rhode Island', 'RI'),
        ('South Carolina', 'SC'),
        ('South Dakota', 'SD'),
        ('Tennessee', 'TN'),
        ('Texas', 'TX'),
        ('Utah', 'UT'),
        ('Vermont', 'VT'),
        ('Virginia', 'VA'),
        ('Washington', 'WA'),
        ('West Virginia', 'WV'),
        ('Wisconsin', 'WI'),
        ('Wyoming', 'WY'),
]


class USState:
    """Object to hold known population data and estimate missing years"""
    name = None
    code = None
    pop_data = {}

    def __init__(self, name, code):
        self.name = name
        self.code = code

    @staticmethod
    def calculate_pop(year, start_year, end_year, start_pop, end_pop):
        """Estimates population for year between two years with known pops"""
        if year < start_year or year > end_year:
            raise Exception('Year is out of range')
        pop_distance = end_pop - start_pop
        year_distance = end_year - start_year
        growth_per_year = pop_distance / year_distance
        years_passed = year - start_year
        total_growth = growth_per_year * years_passed
        return int(round(start_pop + total_growth, 0))

    @property
    def data_years(self):
        """List of all years for which there is data"""
        return sorted(self.pop_data.keys())

    @property
    def earliest_data_year(self):
        """Earliest year for which there is data"""
        return self.data_years[0]

    @property
    def latest_data_year(self):
        """Last year for which there is data"""
        length = len(self.data_years) - 1
        return sorted(self.data_years)[length]

    def add_year_data(self, year, population):
        """Adds known population data for a given year"""
        # if year is not already in, convert
        if type(year) != int:
            year = int(year)
        # first set to float to handle decimals, then round, then set to int
        if type(population) != int:
            population = int(round(float(population), 0))
        self.pop_data[year] = population

    def get_previous_data_year(self, year):
        """Gets year prior to given year for which there is data"""
        previous_year = None
        if year <= self.earliest_data_year:
            return None
        for data_year in self.data_years:
            # if year is not surpassed, save data_year to previous_year
            if year > data_year:
                previous_year = data_year
            # if year is surpassed, break loop
            else:
                break
        return previous_year

    def get_next_data_year(self, year):
        """Gets year after given year for which there is data"""
        if year >= self.latest_data_year:
            return None
        for data_year in self.data_years:
            if year < data_year:
                return data_year

    def get_pop_of_year(self, year):
        """Gives population of year from stored data or calculation"""
        # return nothing if year is earlier or later than extent of data range
        if year < self.earliest_data_year or year > self.latest_data_year:
            return None
        # if population is already known for year, simply return it
        if year in self.pop_data:
            return self.pop_data[year]
        # otherwise, begin calculating linear trajectory
        previous_data_year = self.get_previous_data_year(year)
        next_data_year = self.get_next_data_year(year)
        previous_pop_data = self.pop_data[previous_data_year]
        next_pop_data = self.pop_data[next_data_year]
        return self.calculate_pop(
            year,
            previous_data_year,
            next_data_year,
            previous_pop_data,
            next_pop_data
        )

    def populations(self, start_year, end_year):
        """List of dicts with population records for csv export"""
        pop_records = []
        for year in range(start_year, end_year + 1):
            pop_record = {
                'Year': year,
                'State': self.name,
                'State Code': self.code,
                'Population': None,
                'Estimated': True
            }
            if year in self.pop_data:
                pop_record['Population'] = self.pop_data[year]
                pop_record['Estimated'] = False
            else:
                pop_record['Population'] = self.get_pop_of_year(year)
                # if no pop data is known, set estimated to None
                if pop_record['Population'] is None:
                    pop_record['Estimated'] = None
            pop_records.append(pop_record)
        return pop_records


def process_file_data(
    input_filename,
    output_filename,
    start_year,
    end_year,
    input_state_colname,
    input_year_colname,
    input_pop_colname
):
    """Main function to read file, process, and export to csv"""
    # empty dict to hold objects for each state
    states = {}
    # build full paths of filenames, if not already absolute paths
    if not os.path.isabs(input_filename):
        input_filename = os.path.join(FOLDER_PATH, input_filename)
    if not os.path.isabs(output_filename):
        output_filename = os.path.join(FOLDER_PATH, output_filename)
    if not os.path.exists(input_filename):
        raise Exception('Input file does not exist')
    # create new USState objects at corresponding keys in states dict
    for state in STATE_NAMES:
        states[state[0]] = USState(state[0], state[1])

    # read raw file data and add data of corresponding years to states
    print('Reading raw query results from input csv...')
    with open(input_filename, mode='r+') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for csv_row in csv_reader:
            state = states[csv_row[input_state_colname]]
            state.add_year_data(
                csv_row[input_year_colname],
                csv_row[input_pop_colname]
            )

    # loop through each state and add all population data to export_records
    print('Calculating estimated population for missing years...')
    export_records = []
    for state in states:
        state_population_records = states[state].populations(
            start_year, end_year
        )
        for state_population_record in state_population_records:
            export_records.append(state_population_record)

    # define column header names and open csv file for export
    print('Saving processed population data to export csv...')
    column_names = ['Year', 'State', 'State Code', 'Population', 'Estimated']
    with open(output_filename, mode='w+') as csv_file:
        # create csv writer object and write the header
        csv_writer = csv.DictWriter(csv_file, fieldnames=column_names)
        csv_writer.writeheader()
        # loop through each population record and write as a csv row
        for export_record in export_records:
            csv_writer.writerow(export_record)

    print('Finished!')


def parse_arguments():
    """Reads cmd line arguments"""
    parser = argparse.ArgumentParser(
        description='Processes Wikidata Historic US state population data and \
        estimates population for missing years. Produces a CSV with estimated \
        population for every state for every year between specified years.',
        prog='python {}'.format(os.path.basename(__file__))
    )
    parser.add_argument(
        '-i', '--input',
        nargs=1,
        default=['1_wikidata_query_results.csv'],
        dest='input_filename',
        help='Name of the input file containing results of Wikidata query.'
    )
    parser.add_argument(
        '-o', '--output',
        nargs=1,
        default=['2_wikidata_processed_results.csv'],
        dest='output_filename',
        help='Name of the out file containing processed population data.'
    )
    parser.add_argument(
        '-s', '--start',
        nargs=1,
        default=['1600'],
        dest='start_year',
        help='Year to begin estimating population data.'
    )
    parser.add_argument(
        '-e', '--end',
        nargs=1,
        default=['2018'],
        dest='end_year',
        help='Year to stop estimating population data.'
    )
    parser.add_argument(
        '-c', '--colnames',
        nargs='+',
        default=['stateLabel', 'year', 'population'],
        dest='input_colnames',
        help='Column names on input csv for state, year, and population. \
        MUST be given in that order. Separate each column name with a single\
        space. e.g. --colnames stateLabel year population'
    )
    return parser.parse_args()


if __name__ == '__main__':
    parsed_args = parse_arguments()
    if len(parsed_args.input_colnames) < 3:
        raise Exception('Must specify at least 3 colnames for import csv')
    print(parsed_args.input_filename)
    process_file_data(
        input_filename=parsed_args.input_filename[0],
        output_filename=parsed_args.output_filename[0],
        start_year=int(parsed_args.start_year[0]),
        end_year=int(parsed_args.end_year[0]),
        input_state_colname=parsed_args.input_colnames[0],
        input_year_colname=parsed_args.input_colnames[1],
        input_pop_colname=parsed_args.input_colnames[2]
    )
