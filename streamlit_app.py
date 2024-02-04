import streamlit as st
import pandas as pd
import requests
import snowflake.connector
import folium
 
st.title('Asakawa - A healthy smoothie shop')

st.header('Breakfast Menu')
st.text('🥣Omega 3 & Blueberry Oatmeal')
st.text('🥗Kale, Spinach & Rocket Smoothie')
st.text('🐔Hard-Boiled Free-Range Egg')
st.text('🥑🍞Avocado Toast')

st.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')
my_fruit_list = pd.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Let's put a pick list here so the customer can pick the fruit they want to include
fruits_selected = st.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Banana', 'Pineapple'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

#display the table on the page
if fruits_to_show.empty:
  st.text('Please select the fruits in the drop-down menu above.')
else:
  cal = fruits_to_show['Calories'].sum()
  st.text('The smoothie contains ' +str(cal) + ' calaries.\nThe detailed nutrition information is listed below.')
  st.dataframe(fruits_to_show)

#New Section to display fruityvice api response
st.header('Fruityvice Fruit Advice!')
try:
  fruit_choice = st.text_input('What fruit would you like information about?', 'Kiwi')
  if not fruit_choice:
    streamlit.error('Please type a fruit to get information.')
  else:
    try:
      fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_choice)
      # take the json version of the response and normalize it
      fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
      fruityvice_normalized = fruityvice_normalized.set_index('name')
      fruityvice_normalized = fruityvice_normalized.drop(columns=['id'])
      # output it the screen as a table
      st.dataframe(fruityvice_normalized)
    except KeyError:
      st.error('Please try another fruit name.')
except URLError as e:
  st.error()

st.header("View Our Fruit List - Add Your Favorites!")
# Snowflake-related functions
def get_fruit_load_list():
    with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

# Add a button to load the fruit
if st.button('Get Fruit Load List'):
    my_cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    my_data_rows = get_fruit_load_list()
    my_cnx.close()
    st.dataframe(my_data_rows, column_config={'0':'Name'})

# Allow the end user to add a fruit to the list
def insert_row_snowflake(new_fruit):
    with my_cnx.cursor() as my_cur:
        my_cur.execute("insert into fruit_load_list values ('" + new_fruit +"')")
        return "Thanks for adding " + new_fruit
    
add_my_fruit = st.text_input('What fruit would you like to add?')
if st.button('Add a Fruit to the List'):
    my_cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    back_from_function = insert_row_snowflake(add_my_fruit)
    st.text(back_from_function)
    my_cnx.close()

# Create a map
st.header("Time and venue")
st.text('Pop up shop')
st.text('2500 Chem. de Polytechnique, Montréal, QC H3T 1J4')
# Create a DataFrame with the points you want to highlight
highlight = pd.DataFrame({
    'latitude': [45.5048],
    'longitude': [-73.6132]
}) 
# Add the highlight points to the map
st.map(highlight)

# don't run anything past here while we troubleshoot
st.stop()
