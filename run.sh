#!/bin/bash

# Initialize variables
script="neurons/validator.py"
autoRunLoc=$(readlink -f "$0")
proc_name="vectornet_validator"
args=()
version_location="./vectornet/__init__.py"
version="__version__"

old_args=$@

if ! command -v pm2 &> /dev/null
then
    echo "pm2 could not be found. To install see: https://pm2.keymetrics.io/docs/usage/quick-start/"
    exit 1
fi

version_less_than_or_equal() {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

version_less_than() {
    [ "$1" = "$2" ] && return 1 || version_less_than_or_equal $1 $2
}

get_version_difference() {
    local tag1="$1"
    local tag2="$2"

    local version1=$(echo "$tag1" | sed 's/v//')
    local version2=$(echo "$tag2" | sed 's/v//')

    IFS='.' read -ra version1_arr <<< "$version1"
    IFS='.' read -ra version2_arr <<< "$version2"

    local diff=0
    for i in "${!version1_arr[@]}"; do
        local num1=${version1_arr[$i]}
        local num2=${version2_arr[$i]}

        # Compare the numbers and update the difference
        if (( num1 > num2 )); then
            diff=$((diff + num1 - num2))
        elif (( num1 < num2 )); then
            diff=$((diff + num2 - num1))
        fi
    done

    strip_quotes $diff
}

read_version_value() {
    # Read each line in the file
    while IFS= read -r line; do
        # Check if the line contains the variable name
        if [[ "$line" == *"$version"* ]]; then
            # Extract the value of the variable
            local value=$(echo "$line" | awk -F '=' '{print $2}' | tr -d ' ')
            strip_quotes $value
            return 0
        fi
    done < "$version_location"

    echo ""
}

check_package_installed() {
    local package_name="$1"
    os_name=$(uname -s)

    if [[ "$os_name" == "Linux" ]]; then
        # Use dpkg-query to check if the package is installed
        if dpkg-query -W -f='${Status}' "$package_name" 2>/dev/null | grep -q "installed"; then
            return 1
        else
            return 0
        fi
    elif [[ "$os_name" == "Darwin" ]]; then
         if brew list --formula | grep -q "^$package_name$"; then
            return 1
        else
            return 0
        fi
    else
        echo "Unknown operating system"
        return 0
    fi
}

check_variable_value_on_github() {
    local repo="$1"
    local file_path="$2"
    local variable_name="$3"
    local branch="$4"

    local url="https://api.github.com/repos/$repo/contents/$file_path?ref=$branch"
    local response=$(curl -s "$url")

    if [[ $response =~ "message" ]]; then
        echo "Error: Failed to retrieve file contents from GitHub."
        return 1
    fi

    local content=$(echo "$response" | tr -d '\n' | jq -r '.content')

    if [[ "$content" == "null" ]]; then
        echo "File '$file_path' not found in the repository."
        return 1
    fi

    local decoded_content=$(echo "$content" | base64 --decode)

    local variable_value=$(echo "$decoded_content" | grep "$variable_name" | awk -F '=' '{print $2}' | tr -d ' ')

    if [[ -z "$variable_value" ]]; then
        echo "Variable '$variable_name' not found in the file '$file_path'."
        return 1
    fi

    strip_quotes $variable_value
}

strip_quotes() {
    local input="$1"

    local stripped="${input#\"}"
    stripped="${stripped%\"}"

    echo "$stripped"
}

while [[ $# -gt 0 ]]; do
  arg="$1"

  if [[ "$arg" == -* ]]; then
    if [[ $# -gt 1 && "$2" != -* ]]; then
          if [[ "$arg" == "--script" ]]; then
            script="$2";
            shift 2
        else
            args+=("'$arg'");
            args+=("'$2'");
            shift 2
        fi
    else
      args+=("'$arg'");
      shift
    fi
  else
    args+=("'$arg '");
    shift
  fi
done

echo "Received delay input: $delay seconds."

if [[ -z "$script" ]]; then
    echo "The --script argument is required."
    exit 1
fi

branch=$(git branch --show-current)            # get current branch.
echo watching branch: $branch
echo pm2 process name: $proc_name

current_version=$(read_version_value)

if pm2 status | grep -q $proc_name; then
    echo "The script is already running with pm2. Stopping and restarting..."
    pm2 delete $proc_name
fi


echo "Running $script with the following pm2 config:"

joined_args=$(printf "%s," "${args[@]}")

joined_args=${joined_args%,}

echo "module.exports = {
  apps : [{
    name   : '$proc_name',
    script : '$script',
    interpreter: 'python3',
    min_uptime: '5m',
    max_restarts: '5',
    args: [$joined_args]
  }]
}" > app.config.js

cat app.config.js

pm2 start app.config.js

check_package_installed "jq"
if [ "$?" -eq 1 ]; then
    last_restart_time=$(date +%s)
    restart_interval=$((30 * 3600))  # 30 hours in seconds

    while true; do
        current_time=$(date +%s)
        time_since_last_restart=$((current_time - last_restart_time))

        if [ -d "./.git" ]; then

            latest_version=$(check_variable_value_on_github "vector-pool/vector-store" "vectornet/__init__.py" "__version__ " "$branch")

            if version_less_than $current_version $latest_version; then
                echo "latest version $latest_version"
                echo "current version $current_version"
                sleep $delay # Apply the delay
                
                if git pull origin $branch; then
                    echo "New version published. Updating the local copy."

                    pip install -e .

                    echo "Restarting PM2 process"
                    pm2 restart $proc_name
                    
                    current_version=$(read_version_value)
                    echo ""

                    last_restart_time=$current_time

                    echo "Restarting script..."
                    ./$(basename $0) $old_args && exit
                else
                    echo "**Will not update**"
                    echo "It appears you have made changes on your local copy. Please stash your changes using git stash."
                fi

            else
                echo "**Skipping update **"
                echo "$current_version is the same as or more than $latest_version. You are likely running locally."

                if [ $time_since_last_restart -ge $restart_interval ]; then
                    echo "30 hours passed. Performing periodic PM2 restart..."
                    pm2 restart $proc_name
                    
                    last_restart_time=$current_time
                    echo "Periodic restart completed"
                fi
            fi
        else
            echo "The installation does not appear to be done through Git. Please install from source at https://github.com/opentensor/validators and rerun this script."
        fi
        
        sleep 1800
    done
else
    echo "Missing package 'jq'. Please install it for your system first."
fi