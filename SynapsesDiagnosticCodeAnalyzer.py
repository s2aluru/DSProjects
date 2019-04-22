import pandas as pd
import numpy as np
import Helper

class DiagnosticCodeAnalyzer:

    def __init__(self):
        self.input_file = 'Production.DiagnosisCodeDetail_2014- mar 2019.csv'
        self.patientname = 'Patient Name'
        self.svcdt = 'Date of Service'
        self.diagcode = 'Diagnosis Code '
        self.diag_codes = [self.diagcode + str(i) for i in range(1, 13)]
        self.code = 'Code'
        self.helper = Helper.Utils()

    def read_data(self):
        self.data = pd.read_csv(self.helper.datasetfolder + self.input_file, dtype={'Diagnosis Code 1': str,
                                                           'Diagnosis Description 1': str,
                                                           'Diagnosis Code 2': str,
                                                           'Diagnosis Description 2': str,
                                                           'Diagnosis Code 3': str,
                                                           'Diagnosis Description 3': str,
                                                           'Diagnosis Code 4': str,
                                                           'Diagnosis Description 4': str,
                                                           'Diagnosis Code 5': str,
                                                           'Diagnosis Description 5': str,
                                                           'Diagnosis Code 6': str,
                                                           'Diagnosis Description 6': str,
                                                           'Diagnosis Code 7': str,
                                                           'Diagnosis Description 7': str,
                                                           'Diagnosis Code 8': str,
                                                           'Diagnosis Description 8': str,
                                                           'Diagnosis Code 9': str,
                                                           'Diagnosis Description 9': str,
                                                           'Diagnosis Code 10': str,
                                                           'Diagnosis Description 10': str,
                                                           'Diagnosis Code 11': str,
                                                           'Diagnosis Description 11': str,
                                                           'Diagnosis Code 12': str,
                                                           'Diagnosis Description 12': str}, na_values=[''])
        self.data = self.data.fillna('')
        self.display_info()
        return self.data

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def display_info(self):
        patient_cnt = self.data[self.patientname].nunique()
        self.helper.printHtml('No. of Patients: {}'.format(patient_cnt))
        code_cnt = len(self.total_diagnosiscodes())
        self.helper.printHtml('No. of Diagnosis codes: {}'.format(code_cnt))
        title = 'First 5 out of {} records from the Diagnosis Spreadsheet (just a glimpse)'.format(len(self.data))
        self.helper.display_data(title, self.data, 5)

    def process(self):
        file = "Patient_Diagnosis_Codes"
        self.helper.printHeader(file)
        self.patients_codes()
        dict_sheet = {'Patients and Codes':self.patient_codes,
                      'Codes per Patient': self.codes_per_patient(),
                      'Patients per Code': self.patients_per_codes()}
        self.helper.saveExcel(output_file= file, sheets=dict_sheet)
        return self.patient_codes

    def total_diagnosiscodes(self):
        for i in range(len(self.diag_codes)):
            codes = self.data[self.diag_codes[i]].unique()
            if (i == 0):
                uniquecodes = codes
            else:
                uniquecodes = np.append(uniquecodes, codes, axis=0)
        all_codes_set = list(set(uniquecodes))
        all_codes = [s for s in all_codes_set if type(s) == str and s != '']
        return all_codes

    def patients_codes(self):
        title = 'Patients and Diagnosis Codes'
        data = pd.melt(self.data, id_vars=self.patientname, value_vars=self.diag_codes)[
            [self.patientname, 'value']] \
            .rename(columns={'value': self.code})
        self.patient_codes = data
        self.helper.display_data(title, data, 10)

    def codes_per_patient(self):
        title = 'No. of Codes per Patient'
        data =  self.patient_codes.groupby(by=[self.patientname], as_index=False)[self.code]\
            .count().rename(columns={self.code: 'No. of Codes'})
        self.helper.display_data(title, data, 10)
        return data

    def patients_per_codes(self):
        title = 'No. of Patients per Code'
        data = self.patient_codes.groupby(by=[self.code], as_index=False)[self.patientname]\
            .count().rename(columns={self.patientname: 'No. of Patients'})
        self.helper.display_data(title, data, 10)
        return data