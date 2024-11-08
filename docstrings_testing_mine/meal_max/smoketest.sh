#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meals 
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the database..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  
  echo "Response: $response" 

  if echo "$response" | grep -q '"status": "combatant added"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}


delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}


get_all_songs() {
  echo "Getting all songs in the playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-songs-from-catalog")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All songs retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Songs JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get songs."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}


get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}


############################################################
#
# Battle
#
############################################################
initiate_battle() {
  echo "Initiating battle between two meals..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "battle complete"'; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Battle completed successfully! Winner: $winner"
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initiate battle."
    exit 1
  fi
}


clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    exit 1
  fi
}
prep_combatant() {
  meal_name=$1

  echo "Preparing combatant with meal name: $meal_name..."

  # Properly escape the meal_name to handle any special characters
  payload="{\"meal\": \"$meal_name\"}"

  # Send the POST request with the corrected payload
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "$payload")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Combatant prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatant JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Response: $response" 
    echo "Failed to prepare combatant."
    exit 1
  fi
}





############################################################
#
# Leaderboard
#
############################################################

get_leaderboard() {
  sort_by=$1  # Optional query parameter to specify sorting field

  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by $sort_by):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Meals
create_meal "Spaghetti" "Italian" 12.99 "MED"
create_meal "Chicken" "Indian" 14.99 "HIGH"
create_meal "Tacos" "Mexican" 9.99 "LOW"
create_meal "Sushi" "Japanese" 18.99 "MED"
create_meal "Grilled Cheese" "American" 7.99 "LOW"

delete_meal_by_id 1
get_meal_by_id 2
get_meal_by_name "Chicken"


# Battle
prep_combatant "Sushi"
prep_combatant "Grilled Cheese"
get_combatants
initiate_battle
clear_combatants

# Leaderboard
get_leaderboard "wins"
get_leaderboard "win_pct"

echo "All tests passed successfully!"

