# kgcontroller module
import pandas as pd
import numpy as np
from dbexcel import *
from kgmodel import *
import matplotlib.pyplot as plt


# CRUD metoder

# Create
# pd.append, pd.concat eller df.loc[-1] = [1,2] df.index = df.index + 1 df = df.sort_index()
def insert_foresatt(f):
    # Ikke en god praksis å oppdaterer DataFrame ved enhver endring!
    # DataFrame er ikke egnet som en databasesystem for webapplikasjoner.
    # Vanligvis bruker man databaseapplikasjoner som MySql, Postgresql, sqlite3 e.l.
    # 3 fremgangsmåter for å oppdatere DataFrame:
    # (1) df.colums er [['a', 'b']]
    #     df = pd.concat([pd.DataFrame([[1,2]], columns=df.columns), df], ignore_index=True)
    # (2) df = df.append({'a': 1, 'b': 2}, ignore_index=True)
    # (3) df.loc[-1] = [1,2]
    #     df.index = df.index + 1
    #     df = df.sort_index()
    global forelder
    new_id = 0
    if forelder.empty:
        new_id = 1
    else:
        new_id = forelder['foresatt_id'].max() + 1
    
    # skriv kode for å unngå duplikater
    
    forelder = pd.concat([pd.DataFrame([[new_id,
                                        f.foresatt_navn,
                                        f.foresatt_adresse,
                                        f.foresatt_tlfnr,
                                        f.foresatt_pnr]],
                columns=forelder.columns), forelder], ignore_index=True)
    
    
    return forelder

def insert_barn(b):
    global barn
    new_id = 0
    if barn.empty:
        new_id = 1
    else:
        new_id = barn['barn_id'].max() + 1
    
    # burde også sjekke for samme foresatt_pnr for å unngå duplikater
    
    barn = pd.concat([pd.DataFrame([[new_id,
                                    b.barn_pnr]],
                columns=barn.columns), barn], ignore_index=True)
    
    return barn

def insert_soknad(s):
    """[sok_id, foresatt_1, foresatt_2, barn_1, fr_barnevern, fr_sykd_familie,
    fr_sykd_barn, fr_annet, barnehager_prioritert, sosken__i_barnehagen,
    tidspunkt_oppstart, brutto_inntekt]
    """
    global soknad
    new_id = 0
    if soknad.empty:
        new_id = 1
    else:
        new_id = soknad['sok_id'].max() + 1
    
    
    # burde også sjekke for duplikater
    
    soknad = pd.concat([pd.DataFrame([[new_id,
                                     s.foresatt_1.foresatt_id,
                                     s.foresatt_2.foresatt_id,
                                     s.barn_1.barn_id,
                                     s.fr_barnevern,
                                     s.fr_sykd_familie,
                                     s.fr_sykd_barn,
                                     s.fr_annet,
                                     s.barnehager_prioritert,
                                     s.sosken__i_barnehagen,
                                     s.tidspunkt_oppstart,
                                     s.brutto_inntekt,
                                     s.tilbud]],
                columns=soknad.columns), soknad], ignore_index=True)
    
    return soknad

# ---------------------------
# Read (select)

def select_alle_barnehager():
    """Returnerer en liste med alle barnehager definert i databasen dbexcel."""
    return barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()

def select_foresatt(f_navn):
    """OBS! Ignorerer duplikater"""
    series = forelder[forelder['foresatt_navn'] == f_navn]['foresatt_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series

def select_barn(b_pnr):
    """OBS! Ignorerer duplikater"""
    series = barn[barn['barn_pnr'] == b_pnr]['barn_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series
    
def check_availability():
    kg = pd.read_excel("kgdata.xlsx", sheet_name="barnehage",
                       names=["index", "barnehage_id", "barnehage_navn", "barnehage_antall_plasser", "barnehage_ledige_plasser"])
    kg_soknad = pd.read_excel("kgdata.xlsx", sheet_name="soknad",
                       names=['sok_id',
                       'foresatt_1',
                       'foresatt_2',
                       'barn_1',
                       'fr_barnevern',
                       'fr_sykd_familie',
                       'fr_sykd_barn',
                       'fr_annet',
                       'barnehager_prioritert',
                       'sosken__i_barnehagen',
                       'tidspunkt_oppstart',
                       'brutto_inntekt',
                       'tilbud'])
    prioritet = kg_soknad.loc[0, "barnehager_prioritert"]
    for x in range(len(kg)):
        kg_check = kg.loc[x, "barnehage_navn"]
        if kg_check  == prioritet:
            kg_id = kg.loc[x, "barnehage_id"]
            break
    for x in range(len(kg)):
        if kg.loc[x, "barnehage_id"] == kg_id:
            plasser = kg.loc[x, "barnehage_ledige_plasser"]
            break
    if plasser  > 0:
        fill_kg_places(x, plasser)
        return "Tilbud"
    else:
        return "Avslag"
        
def select_alle_soknader():
    """Returnerer en liste med alle barnehager definert i databasen dbexcel."""
    return soknad.apply(lambda r: Soknad(r['sok_id'],
                             r['foresatt_1'],
                             r['foresatt_2'],
                             r['barn_1'],
                             r['fr_barnevern'],
                             r['fr_sykd_familie'],
                             r['fr_sykd_barn'],
                             r['fr_annet'],
                             r['barnehager_prioritert'],
                             r['sosken__i_barnehagen'],
                             r['tidspunkt_oppstart'],
                             r['brutto_inntekt'],
                             r['tilbud']),
            axis=1).to_list()

def select_alle_foresatte():
    return forelder.apply(lambda r: Foresatt(r['foresatt_id'],
                             r['foresatt_navn'],
                             r['foresatt_adresse'],
                             r['foresatt_tlfnr'],
                             r['foresatt_pnr']),
            axis=1).to_list()

def select_alle_barn():
    return barn.apply(lambda r: Barn(r['barn_id'],
                             r['barn_pnr']),
            axis=1).to_list()
                             
# --- Skriv kode for select_soknad her
def statestikk():
    kgdata = pd.read_excel("ssb-barnehager-2015-2023-alder-1-2-aar.xlsm", sheet_name="KOSandel120000",
                       header=3,
                       names=["kom","y15","y16","y17","y18","y19","y20","y21","y22","y23"],
                       na_values=[".", ".."])



#hvilken kommune
    valgt_kommune = "4203 Arendal" 
    data_for_kommune = kgdata[kgdata["kom"] == valgt_kommune]

# Beregn prosentandel av barn 1 -2 år
    prosent_barn = data_for_kommune[["y15", "y16", "y17", "y18", "y19", "y20", "y21", "y22", "y23"]].values.flatten()

# År
    år = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]

# Lag søylediagram
    fig = plt.figure(figsize=(10, 5))
    plt.bar(år, prosent_barn, color="pink")
    plt.title("Prosent av barn i ett- og to-årsalderen i barnehagen for Arendal (2020-2023)")
    plt.xlabel("År")
    plt.ylabel("Prosent")
    plt.xticks(rotation=45)
    plt.grid(axis="y")
    plt.tight_layout()
    fig.savefig('barnehage/static/images/my_plot.png')
    

# ------------------
# Update
def update_soknad():
     with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:
         soknad.to_excel(writer, sheet_name='soknad')

def fill_kg_places(index_nr, plasser):
    barnehage.at[index_nr, "barnehage_ledige_plasser"] = plasser - 1
    soknad.at[0, "tilbud"] = "Ja"
    with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:
        barnehage.to_excel(writer, sheet_name='barnehage')
    with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:
        soknad.to_excel(writer, sheet_name='soknad')
# ------------------
# Delete


# ----- Persistent lagring ------
def commit_all():
    """Skriver alle dataframes til excel"""
    with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:  
        forelder.to_excel(writer, sheet_name='foresatt')
        barnehage.to_excel(writer, sheet_name='barnehage')
        barn.to_excel(writer, sheet_name='barn')
        soknad.to_excel(writer, sheet_name='soknad')
        
# --- Diverse hjelpefunksjoner ---
def form_to_object_soknad(sd):
    """sd - formdata for soknad, type: ImmutableMultiDict fra werkzeug.datastructures
Eksempel:
ImmutableMultiDict([('navn_forelder_1', 'asdf'),
('navn_forelder_2', ''),
('adresse_forelder_1', 'adf'),
('adresse_forelder_2', 'adf'),
('tlf_nr_forelder_1', 'asdfsaf'),
('tlf_nr_forelder_2', ''),
('personnummer_forelder_1', ''),
('personnummer_forelder_2', ''),
('personnummer_barnet_1', '234341334'),
('personnummer_barnet_2', ''),
('fortrinnsrett_barnevern', 'on'),
('fortrinnsrett_sykdom_i_familien', 'on'),
('fortrinnsrett_sykdome_paa_barnet', 'on'),
('fortrinssrett_annet', ''),
('liste_over_barnehager_prioritert_5', ''),
('tidspunkt_for_oppstart', ''),
('brutto_inntekt_husholdning', '')])
    """
    # Lagring i hurtigminne av informasjon om foreldrene (OBS! takler ikke flere foresatte)
    foresatt_1 = Foresatt(0,
                          sd.get('navn_forelder_1'),
                          sd.get('adresse_forelder_1'),
                          sd.get('tlf_nr_forelder_1'),
                          sd.get('personnummer_forelder_1'))
    insert_foresatt(foresatt_1)
    foresatt_2 = Foresatt(0,
                          sd.get('navn_forelder_2'),
                          sd.get('adresse_forelder_2'),
                          sd.get('tlf_nr_forelder_2'),
                          sd.get('personnummer_forelder_2'))
    insert_foresatt(foresatt_2) 
    
    # Dette er ikke elegang; kunne returnert den nye id-en fra insert_ metodene?
    foresatt_1.foresatt_id = select_foresatt(sd.get('navn_forelder_1'))
    foresatt_2.foresatt_id = select_foresatt(sd.get('navn_forelder_2'))
    
    # Lagring i hurtigminne av informasjon om barn (OBS! kun ett barn blir lagret)
    barn_1 = Barn(0, sd.get('personnummer_barnet_1'))
    insert_barn(barn_1)
    barn_1.barn_id = select_barn(sd.get('personnummer_barnet_1'))
    
    # Lagring i hurtigminne av all informasjon for en søknad (OBS! ingen feilsjekk / alternativer)
        
    sok_1 = Soknad(0,
                   foresatt_1,
                   foresatt_2,
                   barn_1,
                   sd.get('fortrinnsrett_barnevern'),
                   sd.get('fortrinnsrett_sykdom_i_familien'),
                   sd.get('fortrinnsrett_sykdome_paa_barnet'),
                   sd.get('fortrinssrett_annet'),
                   sd.get('liste_over_barnehager_prioritert_5'),
                   sd.get('har_sosken_som_gaar_i_barnehagen'),
                   sd.get('tidspunkt_for_oppstart'),
                   sd.get('brutto_inntekt_husholdning'),
                   sd.get('tilbud'))
    
    return sok_1

# Testing
def test_df_to_object_list():
    assert barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()[0].barnehage_navn == "Sunshine Preschool"