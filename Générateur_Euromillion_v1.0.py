import os
import xlrd
import random
import requests
import time
import math
import numpy as np
import qiskit
from bs4 import BeautifulSoup
from qiskit import Aer, execute
from sklearn.linear_model import LinearRegression
from qiskit.circuit.library import QuantumVolume
from qiskit.circuit.library import RYGate

# Set parameters
num_samples = 1000  # <-- Définir num_samples

# Définir la fonction de génération quantique
def generate_quantum_numbers(num_samples):
    # Créer un circuit de variété quantique
    circuit = QuantumVolume(5, seed_transpiler=42).decompose().compose(qiskit.circuit.library.RYGate(math.pi/4).control(4))

    # Définir le simulateur quantique
    backend = qiskit.providers.aer.QasmSimulator.from_backend(Aer.get_backend('qasm_simulator')).with_qrng("legacy-acorn")
    num_shots = 8192

    # Exécuter le circuit plusieurs fois pour générer des nombres pseudo-aléatoires
    job = execute(circuit, backend, shots=num_shots)
    result = job.result()

    # Vérifier si la clé 'counts' est présente dans le dictionnaire avant de l'appeler
    if not result.results or 'counts' not in result.results[0].to_dict():
        raise ValueError("Error: no counts for any experiment")

    counts = result.results[0].to_dict()['counts']
    if not counts:
        raise ValueError("Error: no counts for any experiment")
    valid_counts={}

    for k, v in counts.items ():
        if sum ( v ) >= 100:
            valid_counts[k]=v
    numbers=[int ( k, 2 ) for k in valid_counts.keys ()]
    return numbers


# Historique FDJ
def recent_numbers(last_draws, num_samples):
    """Returns the n most recently drawn numbers."""
    last_draws.sort(reverse=True)
    recent_numbers = []
    for draw in last_draws:
        if len(recent_numbers) == num_samples:
            break
        if draw not in recent_numbers:
            recent_numbers.append(draw)
    return recent_numbers


main_ball_last_draws = [5, 9, 17, 23, 30]
most_recent_main_balls = recent_numbers(main_ball_last_draws, num_samples)


def most_frequent_numbers(numbers, num_samples):
    """Returns the n most frequent numbers among a list of lottery numbers."""
    freq_dict = {}
    for number in numbers:
        if number in freq_dict:
            freq_dict[number] += 1
        else:
            freq_dict[number] = 1
    sorted_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True)}
    most_freq = list(sorted_dict.keys())[:num_samples]
    return most_freq


most_recent_main_balls = recent_numbers(main_ball_last_draws, num_samples)
selected_main_balls = set(most_recent_main_balls + most_recent_main_balls)

# Set parameters
ball_mass=65  # in grams
ball_diameter=5  # in cm
sphere_diameter=70  # in cm

# Calculate ball volume
ball_volume=4 / 3 * math.pi * (ball_diameter / 2) ** 3

# Calculate sphere volume
sphere_volume=4 / 3 * math.pi * (sphere_diameter / 2) ** 3

# Calculate number of balls that can fit in the sphere
packing_fraction=0.74  # Facteur de compacité pour les sphères (empilement hexagonal compact)
num_balls_in_sphere=int ( (sphere_volume * packing_fraction) // ball_volume )

# Define the number of balls to draw
num_main_balls=min ( 5, num_balls_in_sphere )  # maximum of 5 balls or the number of balls that can fit in the sphere
num_lucky_stars=2

# Load the ball and lucky star frequencies from the Excel files
workbook = xlrd.open_workbook('number.xls')
sheet = workbook.sheet_by_index(0)

# Extract main ball numbers and frequencies
main_ball_numbers = [int(sheet.cell_value(row_index, 0)) for row_index in range(1, sheet.nrows)]
main_ball_frequencies = [sheet.cell_value(row_index, 1) for row_index in range(1, sheet.nrows)]


def check_frequencies(frequencies):
    if len ( frequencies ) == 0:
        return False
    first_digit_frequencies=[0] * 9
    for f in frequencies:
        if f > 0:
            first_digit=int ( str ( f )[0] )
            first_digit_frequencies[first_digit - 1]+=1
    expected_frequencies=[math.log10 ( 1 + 1 / d ) * len ( frequencies ) for d in range ( 1, 10 )]
    chi_squared_statistic=sum ( [abs ( f - o ) / o for f, o in zip ( first_digit_frequencies, expected_frequencies )] )
    degrees_of_freedom=len ( first_digit_frequencies ) - 2
    critical_value=21.67
    return chi_squared_statistic <= critical_value


main_ball_numbers=[int ( sheet.cell_value ( row_index, 0 ) ) for row_index in range ( 1, sheet.nrows )]
main_ball_frequencies=[sheet.cell_value ( row_index, 1 ) for row_index in range ( 1, sheet.nrows )]
main_ball_last_draws=[sheet.cell_value ( row_index, 3 ) for row_index in range ( 1, sheet.nrows )]

lucky_star_numbers=[]
lucky_star_frequencies=[]
lucky_star_last_draws=[]

workbook=xlrd.open_workbook ( 'stars.xls' )
sheet=workbook.sheet_by_index ( 0 )

lucky_star_numbers=[int ( sheet.cell_value ( row_index, 0 ) ) for row_index in range ( 1, sheet.nrows )]
lucky_star_frequencies=[sheet.cell_value ( row_index, 1 ) for row_index in range ( 1, sheet.nrows )]
lucky_star_last_draws=[sheet.cell_value ( row_index, 3 ) for row_index in range ( 1, sheet.nrows )]

if not check_frequencies ( main_ball_frequencies ):
    print ( "The main ball frequencies do not conform to Benford's law." )
if not check_frequencies ( lucky_star_frequencies ):
    print ( "The lucky star frequencies do not conform to Benford's law." )

exclude_balls=[]

workbook=xlrd.open_workbook ( 'stars.xls' )
sheet=workbook.sheet_by_index ( 0 )

lucky_star_numbers=[int ( sheet.cell_value ( row_index, 0 ) ) for row_index in range ( 1, sheet.nrows )]
lucky_star_frequencies=[sheet.cell_value ( row_index, 1 ) for row_index in range ( 1, sheet.nrows )]
lucky_star_last_draws=[sheet.cell_value ( row_index, 3 ) for row_index in range ( 1, sheet.nrows )]

lucky_star_frequencies=[]
last_draw_dates=[]
for row_index in range ( 1, sheet.nrows ):
    lucky_star_frequencies.append ( sheet.cell_value ( row_index, 1 ) )
    last_draw_dates.append ( sheet.cell_value ( row_index, 3 ) )

# Define the Euromillions balls and lucky stars
main_balls=list ( range ( 1, 51 ) )
lucky_stars=list ( range ( 1, 13 ) )

# Get the last Euromillions result from the FDJ website
url="https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/resultats"
page=requests.get ( url )
soup=BeautifulSoup ( page.content, "html.parser" )

# Extract the winning numbers and lucky stars from the webpage
winning_numbers=[]
winning_lucky_stars=[]
for div in soup.find_all ( 'div', {'class': 'rslt-nb'} ):
    for span in div.find_all ( 'span' ):
        number=int ( span.get_text () )
        if len ( winning_numbers ) < 5:
            winning_numbers.append ( number )
        else:
            winning_lucky_stars.append ( number )

# Remove winning numbers and lucky stars from the possible choices
for number in winning_numbers:
    if number in main_balls:
        main_balls.remove ( number )
    if number in exclude_balls:
        exclude_balls.remove ( number )

for star in winning_lucky_stars:
    if star in lucky_stars:
        lucky_stars.remove ( star )
    if star in exclude_stars:
        exclude_stars.remove ( star )

# Effacer l'écran
os.system('cls' if os.name == 'nt' else 'clear')

# Ask for user input to generate the Euromillions numbers

print ( "" )
print ( "############################################################" )
print ( "####################### AVHIRAL TE@M #######################" )
print ( "############################################################" )
print ( "############### GENERATOR EUROMILLION V1.0 #################" )
print ( "############################################################" )
print ( "################### CODE : DAVID PILATO ####################" )
print ( "############################################################" )
print ( "" )
print("\033[36m# Option calculs de simulation active et utilisé V1.0 #")
print ( "" )
print ( "\033[33mEntrez les cinq numéros gagnants sorties la dernière fois (séparés par des espaces): " )
print ( "" )
user_main_balls=input ().split ()
user_main_balls=[int ( x ) for x in user_main_balls]

print ( "" )

print ( "\033[33mEntrez les deux étoiles gagnantes sorties la dernière fois (séparés par des espaces): " )
print ( "" )
user_lucky_stars=input ().split ()
user_lucky_stars=[int ( x ) for x in user_lucky_stars]

print ( "" )

# Define the Euromillions balls and lucky stars to exclude
exclude_balls=user_main_balls + winning_numbers
exclude_stars=user_lucky_stars + winning_lucky_stars

# Draw the main balls
main_balls_drawn=np.random.choice ( main_balls, size=num_main_balls, replace=False,
                                    p=np.array ( main_ball_frequencies ) / sum ( main_ball_frequencies ) )

# Draw the lucky stars
lucky_stars_drawn=np.random.choice ( lucky_stars, size=num_lucky_stars, replace=False,
                                     p=np.array ( lucky_star_frequencies ) / sum ( lucky_star_frequencies ) )

# Define the number of balls and mixing time
num_balls=len ( main_balls ) + len ( lucky_stars )  # total number of balls in the machine
mixing_time=10  # time in seconds to simulate ball mixing

# Define the range of possible rotation speeds for balls and stars
ball_speed_range=(5, 10)  # in revolutions per second
star_speed_range=(10, 20)  # in revolutions per second

# Compute the rotation time for balls and stars
ball_rotation_time=1 / num_balls
star_rotation_time=1 / len ( lucky_stars )

# Importer les bibliothèques nécessaires pour la génération quantique
from qiskit import Aer, execute
from qiskit.circuit.library import QuantumVolume


def simulate_mixing_time(speed_range, rotation_time, mixing_time):
    speeds=np.arange ( speed_range[0], speed_range[1], rotation_time )
    time_per_speed=mixing_time / len ( speeds )
    mixed_numbers=np.repeat ( np.arange ( 1, len ( speeds ) + 1 ), np.ceil ( time_per_speed ) )
    np.random.shuffle ( mixed_numbers )
    return mixed_numbers


# Utilisez cette fonction pour simuler le mélange des balles principales et des étoiles porte-bonheur :
mixed_main_balls=simulate_mixing_time ( ball_speed_range, ball_rotation_time, mixing_time )[
                 :min ( len ( main_balls_drawn ), num_main_balls )]
mixed_lucky_stars=simulate_mixing_time ( star_speed_range, star_rotation_time, mixing_time )[
                  :min ( len ( lucky_stars_drawn ), num_lucky_stars )]

# Utilisez les indices mélangés pour sélectionner les numéros gagnants :
main_balls_drawn=main_balls_drawn[:min ( len ( mixed_main_balls ), num_main_balls )]
lucky_stars_drawn=lucky_stars_drawn[:min ( len ( mixed_lucky_stars ), num_lucky_stars )]

# Print the results
print ( "\033[93m" )
print ( f"\nLes numéros Euromillions avec estimation tirés sont: " )
print ( "\033[37m" )
print ( f"Balles principales : {sorted ( main_balls_drawn )}" )
print ( f"Bonnes étoiles : {sorted ( lucky_stars_drawn )}" )

# Print the user's numbers
print ( "\033[93m" )
print ( f"\nLes derniers numéros tirés gagnants sont: " )
print ( "\033[37m" )
print ( f"Balles principales: {sorted ( user_main_balls )}" )
print ( f"Bonnes étoiles: {sorted ( user_lucky_stars )}" )

# Check the user's numbers against the last result
num_correct_main_balls=len ( set ( winning_numbers ).intersection ( set ( user_main_balls ) ) )
num_correct_lucky_stars=len ( set ( winning_lucky_stars ).intersection ( set ( user_lucky_stars ) ) )

# End
print ( "" )
print ( "Appuyez [Entrer] pour fermer le programme" )
pause=input ()
