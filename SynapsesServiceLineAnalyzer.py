import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import Helper

class ServiceLineAnalyzer:
    
    referprovider = 'Referring Provider'
    location = 'Location Name'
    proccode = 'Procedure Code'
    modifier = 'Modifier'
    patientname = 'Patient Name'
    primarypayer = 'Primary Payer Name'
    secondarypayer = 'Secondary Payer Name'
    charge = 'Charge'
    adjustment = 'Adjustment'
    patientresp = 'Patient Responsiblity'
    writeoff =  'Write Off'
    insurancepayment = 'Insurance Payment'
    patientpayment = 'Patient Payment'
    overpayment = 'Overpayment'
    totalpayment = 'Total Payment'
    svcdt = 'Date of Service'
    svc_dt  = 'Date_of_Service'
    svcyr = 'Year of Service'
    svc_yr = 'Year_of_Service'
    selfpay = 'Self Pay'
    selfpayval = 'SELF PAY'
    billable = 'Billable'
    ref_prov_name = 'Referring_Provider_Name'
    patient_name ='Patient_Name'
    data = None
    count = 'Count'
    total = 'Total'

    numeric_cols = [charge, adjustment, patientresp, writeoff, insurancepayment, patientpayment, overpayment, totalpayment]
      
    unique_columns = [referprovider, location, proccode, modifier, patientname, primarypayer, secondarypayer]
        
    non_billable_codes = ['NSEMG', 'FMLA', 'NSEEG', 'NSF', 'VES', 'EEGNS', 'FORMS', 'DC', 
                         'IME', 'NRP', 'ATT', 'MRINS', 'WCFORM', 'NR', 'MRL', 'MR', 'DIS']

    billable_codes = ['99214', '99213',  '99204', '95886', '95909', '99212', '95910', '95885', '99205', '95911', 
                   '99203', '95908', '99222', '95819', '95816', '99215', '95912', '99223', '99233', '99235', 
                   '99232', '64615', 'J0585',  '95913', '99202',  '95813', '99234', '99224', '99225',  '99284',
                   '95866', '95937', '64616', '99291']
     
    
    def __init__(self):
        self.datasetfolder = "C:\\Users\\spunna\\Data Science\\SynapsesAnalytics\\Data\\"
        self.input_file = 'Production Report by Service Line Analysis 2014 - jan 2019.csv'
        self.helper = Helper.Utils()
        
    def read_data(self):
        self.data = pd.read_csv(self.datasetfolder + self.input_file)
        self.columns = self.data.columns
        self.clean_datatypes()
        self.add_columns()
        self.display_info()
        return self.data

    def write_data(self, data):
        self.data = data
    
    def process_basic(self):
        self.get_unique_values()
        self.self_pay_counts()
        self.billable_counts()      
       # self.referring_providers()
       
    def process_counts(self):
        self.helper.printHtml('Following analysis is for reference, output is not part of Excel file.')
        self.procedure_counts(100)
        self.primary_payer_counts(100)
        self.referring_providers_counts(100)
        #self.top_billable_procedure_codes(100)
        
    def process_payments(self, save_excel):

        if (save_excel):
            file = 'Payments'
            self.helper.printHeader(file)

        procedures = self.merge_procedures(self.payment_by_procedure(True), self.payment_by_procedure(False))
        bypayer = self.merge_patient_procedure_payer(self.patients_by_providers(), self.procedures_by_providers())

        sp_vs_insured_allyears = self.selfpay_vs_insured_by_procedure_param(True)
        allyearsfile = self.payer_payment_by_procedure(True, False)
        lastyearfile = self.payer_payment_by_procedure(False, False)

       # allyearsbillablefile = self.payer_payment_by_procedure(True, True)
       # lastyearbillablefile = self.payer_payment_by_procedure(False, True)

        if ( save_excel):
            dict_sheet = {'Payments All Years': procedures,
                        'Patient and Procedure Counts': bypayer,
                        'Insured vs Self Pay All Years' : sp_vs_insured_allyears,
                        'Payment By Code All Years': allyearsfile,
                        'Payment By Code 2018': lastyearfile
                         }
            self.helper.saveExcel(output_file = file, sheets = dict_sheet)
        return sp_vs_insured_allyears

    def merge_procedures(self, a, b):
        c = a.merge(b, on='Procedure Code', how='left', suffixes=('_l', '_r')).drop_duplicates()
        c = c.fillna('')
        c = c.rename(columns={'Total Payment_l': 'Total Payment',
                          'Patient Payment_l': 'Patient Payment',
                          'Insurance Payment_l': 'Insurance Payment',
                          'No. of Services_l': 'No. of Services',
                          'Total Payment x Services_l': 'Total Payment x Services',
                          'Total Payment_r': 'Total Payment 2018',
                          'Patient Payment_r': 'Patient Payment 2018',
                          'Insurance Payment_r': 'Insurance Payment 2018',
                          'No. of Services_r': 'No. of Services  2018',
                          'Total Payment x Services_r': 'Total Payment x Services 2018'})
        return c

    def merge_patient_procedure_payer(self, a, b):
        type = 'Count Type'
        a[type] = 'Patient'
        b[type] = 'Procedure'
        c = a.append(b).sort_values(by=[self.primarypayer, type])
        newcols = [self.primarypayer, type, 2014, 2015, 2016, 2017, 2018, 2019]
        c = c[newcols]
        return c

    def display_info(self):
         self.helper.printHtml('<b>Billable Codes:</b> {}'.format(', '.join(self.billable_codes)), bold = False)
         self.helper.printHtml('<b>Non-Billable Codes:</b> {}'.format(', '.join(self.non_billable_codes)), bold = False)
         self.helper.printHtml('A patient is considered self-pay if primary payer is noted as SELF PAY.', bold = False)
         title = 'First 5 out of {} records from the Analysis Spreadsheet (just a glimpse)</b>'.format(len(self.data))
         self.helper.display_data(title, self.data, 5)
            
    def get_data(self):
        return self.data

    def clean_datatypes(self):
        # change amount columns to numeric
        for col in self.numeric_cols:
            self.data[col] = self.data[col].apply(self.helper.extract_numeric)
         
        # change service to date        
        self.data[self.svcdt] = pd.to_datetime(self.data[self.svcdt])
    
    def is_self_pay(self, row):
        return 'Yes' if (row[self.primarypayer] == self.selfpayval) else 'No'

    def is_billable(self, row):
        return 'Yes' if (row[self.proccode] in self.billable_codes) else 'No'
           
    def add_columns(self):
        
        self.data[self.svcyr] = self.data[self.svcdt].dt.to_period("Y").astype(str).astype(int)
        self.data[self.selfpay] = self.data.apply(self.is_self_pay, axis=1)
        self.data[self.billable] = self.data.apply(self.is_billable, axis=1)

    def save_excel_sheet(self, sheet, data, excel_writer):
        data.to_excel(excel_writer, sheet, data)

    def close_excel_sheet(self, excel_writer):
        excel_writer.close()
        excel_writer.save()

    def column_counts(self, column, count,):
        c = self.data.groupby(self.svcyr)[column].value_counts()
        f = pd.DataFrame(c[c > count])
        return f.rename(columns={column:'Count'}), f
    
    def lineplot(self, dataset, width=16, height=5, xlabel=None, ylabel=None):
        fg,ax = plt.subplots(figsize=(width, height))
        sns.lineplot(data=dataset)
        if ( ylabel != None):
            ax.set_ylabel(ylabel)
        if ( xlabel != None):
            ax.set_xlabel(xlabel)
        plt.setp(ax.get_xticklabels(), rotation=30)
        plt.show();     
    
    def get_unique_values(self):
        data = self.data.groupby(self.svcyr).agg({'Date of Service': 'size',
                                                    'Billable':self.billable_count,
                                                    'Patient Name': 'nunique', 
                                                  'Referring Provider':'nunique',
                                                  'Location Name': 'nunique', 
                                                  'Procedure Code': 'nunique', 
                                                  'Modifier': 'nunique',
                                                  'Primary Payer Name': 'nunique', 'Secondary Payer Name': 'nunique',
                                                
                                                }).rename(columns={'Date of Service': 'Total Services',
                                                                   'Patient Name': 'Patients',
                                                                   'Location Name': 'Locations',
                                                                   'Procedure Code': 'Procedures',
                                                                   'Referring Provider': 'Referring Providers',
                                                                   'Primary Payer Name': 'Primary Payers',
                                                                   'Secondary Payer Name': 'Secondary Payers',
                                                                   'Total Payment': 'Avg Total Payment',
                                                                   'Billable': 'Billable Services'
                                                                  })
        self.helper.display_data('No. of distinct values per year', data, None)
    
        
    def top_billable_procedure_codes(self, count):
        criteria = self.data[self.proccode].isin(self.billable_codes)
        pay_agg = self.data[self.data[self.billable] == True].groupby([self.proccode]).agg({self.totalpayment:'mean'})
        f =  pay_agg.sort_values(self.totalpasyment, ascending=False)[0:count]
        self.lineplot(f, width=20, ylabel='Amount')
        self.helper.display_data('Top {} paid procedure codes'.format(count), f.reset_index(), None)

    def referring_providers_counts(self, count):
        header = 'Providers that referred more than {} times'.format(count)
        data, _ = self.column_counts(self.referprovider, count)
        self.helper.display_data(header, data, None)
    
    def referring_providers(self):
        file = 'Referring Providers'
        self.helper.printHeader(file)
        c = self.data[self.referprovider].value_counts().reset_index()
        data = pd.DataFrame(c.rename(columns={'index':'Provider', self.referprovider:'No. of Referrals'}))
        self.helper.saveExcel(file, sheets= {'Referring Providers': data})
        self.helper.display_data('All the referring providers and no. of their referrals', data, 10)
      
    def procedure_counts(self, count):
        header = 'Procedures occurred more than {} times'.format(count)
        data, _ = self.column_counts(self.proccode, count)
        self.helper.display_data(header, data, None)
    
    def primary_payer_counts(self, count):
        header = 'Primary payers that paid more than {} times'.format(count)
        data, _ = self.column_counts(self.primarypayer, count)
        self.helper.display_data(header, data, None)
        
    def payment_by_procedure(self, allyears):
        title = 'Average Payment for billable procedures for {}'.format('all years' if allyears == True else '2018')
        q = self.data[self.billable] == 'Yes'
        if (allyears == False):
            q = (q) & (self.data[self.svcyr] == 2018)
        f = self.data[q].groupby(self.proccode).agg({self.totalpayment: 'mean', 
                                                     self.patientpayment: 'mean', 
                                                     self.insurancepayment:'mean',
                                                        self.svcdt: 'size'
                                                    }).rename(columns={'Date of Service': 'No. of Services'})
        self.lineplot(f, ylabel= 'Amount')
        f[self.patientpayment] = f[self.patientpayment].astype(int)
        f[self.insurancepayment] = f[self.insurancepayment].astype(int)
        f[self.totalpayment] = f[self.totalpayment].astype(int)
        f['Total Payment x Services'] = f[self.totalpayment]*f['No. of Services']
        data = f.sort_values(self.totalpayment, ascending=False) 
        self.helper.display_data(title, data, None)
        return data.reset_index()
    
    def barplot(self, column, title):
        fg,ax = plt.subplots(figsize=(6,4))
        f = self.data.groupby(self.svcyr)[column].value_counts().unstack().plot(kind='bar', ax=ax);
        plt.setp(ax.get_xticklabels(), rotation=0);
        plt.ylabel('Total Count')
        plt.title(title)
        plt.show();
    
    def self_pay_counts(self):
        self.barplot(self.selfpay, 'Self Pay vs Insured Payers')

    def billable_counts(self):
        self.barplot(self.billable, 'Billable vs Non-Billable Procedure Codes')   
    
    def filter_column(self, column, value):
        return (self.data[column] == value) 
                
    def selfpay_vs_insured_by_procedure_param(self, allyears):
        year = 'all years' if allyears == True else '2018'
        title = 'Insured Patients vs Self Pay by billable procedures for '+year
        #query = (self.data[sla.billable] == 'Yes') 
        if (allyears == False):
            pay_data =self.data[self.data[self.svcyr] == 2018]
        else:
            pay_data = self.data
        self_agg = pay_data.groupby([self.svcyr, self.proccode, self.selfpay])[self.selfpay].count()
        data = self_agg.unstack().fillna(0).astype(int).sort_values(by=[self.svcyr, self.proccode])
        self.helper.display_data(title, data, 20)
        s = data.reset_index().rename(columns={'No': 'Insured', 'Yes': 'Self Pay'})
     
        # empty duplicate year of service columns to write to csv
        #s.loc[s.duplicated(self.svcyr), self.svcyr] = ''
        #s = pd.pivot_table(s, index=['Procedure Code'], columns=[self.svcyr], values=['Insured', 'Self Pay']).fillna('')
        return s
        
    def payer_payment_by_procedure(self, allyears, billable_only):
        year = 'all years' if allyears == True else '2018'
        bill = 'billable' if billable_only == True else 'all'
        title = 'Insurance Average Payments for {} procedures for {}'.format(bill, year)
     
        pay_data = self.data
        if (billable_only == True):
            query = self.filter_column(self.billable, 'Yes')
            pay_data = pay_data[query]
            
        if (allyears == False):
            query = self.filter_column(self.svcyr, 2018)
            pay_data = pay_data[query]
     
        pay_grouped = pay_data.groupby([self.proccode, self.primarypayer])
        pay_agg = pay_grouped.agg({self.insurancepayment :'mean',
                                   self.patientpayment:'mean',
                                   self.totalpayment: 'mean',
                                   self.svcdt: 'size'}).rename(columns={'Date of Service': 'No. of Services'})
        
        f =  pay_agg.sort_values(by=[self.proccode, self.insurancepayment], ascending=False)
        f[self.totalpayment] = f[self.totalpayment].astype(int)
        f[self.patientpayment] = f[self.patientpayment].astype(int)
        f[self.insurancepayment] = f[self.insurancepayment].astype(int)
        f['Insurance Payment x Services'] = f[self.insurancepayment]*f['No. of Services']
        
        self.helper.display_data(title, f, 10)

        s = f.reset_index()
        # empty duplicate procedure code columns to write to csv
        #s.loc[s.duplicated(self.proccode), self.proccode] = '' 
        return s
    
    def billable_count(self, series):
        return series[series == 'Yes'].count()

    def patients_by_providers(self):
        agg =  self.data.groupby(by=[self.svcyr, self.primarypayer]).agg({self.patientname:'nunique'}).reset_index()
        payer_patient = pd.pivot_table(agg, index=self.primarypayer, columns=self.svcyr, values=self.patientname)
        payer_patient = payer_patient.fillna('')
        self.helper.display_data('Patients served by Providers per year', payer_patient, 10)
        return payer_patient.reset_index()

    def procedures_by_providers(self):
        agg = self.data.groupby(by=[self.svcyr, self.primarypayer]).agg({self.proccode: 'nunique'}).reset_index()
        payer_code = pd.pivot_table(agg, index=self.primarypayer, columns=self.svcyr, values=self.proccode)
        payer_code = payer_code.fillna('')
        self.helper.display_data('Procedures by Providers per year', payer_code, 10)
        return payer_code.reset_index()
    
    def process_referring_providers(self):
        file = 'Referring_Providers_Address'
        self.helper.printHeader(file)
        self.refprovdata = pd.read_csv(self.datasetfolder + 'ReferringProviderPatient_Demographics_2019-04-09.csv')
        self.refprovdata.fillna('')
        self.refprovdata.columns = [c.replace(' ', "_") for c in self.refprovdata.columns]
        self.refprovdata[self.svc_dt] = pd.to_datetime(self.refprovdata[self.svc_dt])
        self.refprovdata[self.svc_yr] = self.refprovdata[self.svc_dt].dt.to_period("Y").astype(str).astype(int)

        self.helper.display_data('Referring Providers dataset', self.refprovdata, 5)

        # group providers by year and NPI
        agg2 = self.refprovdata.groupby(by=[self.svc_yr, 'Referring_Provider_NPI'], as_index=False)[self.patient_name] \
            .count().rename(columns={self.patient_name: self.count})

        # group providers NPI into column Total and add dataset to byyear
        agg3 = agg2.groupby('Referring_Provider_NPI', as_index=False)[self.count].sum()
        agg3[self.svc_yr] = self.total
        agg4 = agg2.append(agg3, ignore_index=True)

        # convert year crow to column
        agg5 = pd.pivot_table(agg4, index='Referring_Provider_NPI',
                              columns=self.svc_yr,
                              values=self.count)
        agg5 = agg5.fillna('').reset_index()

        # merge provider address to the group
        need_columns = ['Referring_Provider_Name', 'Referring_Provider_NPI',
                            'Referring_Provider_Phone', 'Referring_Provider_Address_1',
                            'Referring_Provider_Address_2', 'Referring_Provider_City',
                            'Referring_Provider_State', 'Referring_Provider_Zip']
        prov_data = self.refprovdata[need_columns]
        agg6 = agg5.merge(prov_data, on=('Referring_Provider_NPI'), how='left', suffixes=('_l', '_r')).drop_duplicates()

        # reoroder columns and sort by max referal count
        newcols = ['Referring_Provider_Name', 2014, 2015, 2016, 2017, 2018, 2019, 'Total', 'Referring_Provider_NPI',
                   'Referring_Provider_Phone', 'Referring_Provider_Address_1', 'Referring_Provider_Address_2',
                   'Referring_Provider_City', 'Referring_Provider_State', 'Referring_Provider_Zip']
        agg7 = agg6[newcols].sort_values(by=[self.total], ascending=False)

        self.helper.display_data('Referring Providers Analysis', agg7, 5)
        self.helper.saveExcel(file, {'Referring Providers': agg7})


#sla = ServiceLineAnalyzer()
#sla.write_data(opdata)
#s = sla.process_payments()
