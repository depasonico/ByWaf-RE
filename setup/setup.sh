#!/bin/bash


# Global Variables
arch="$(uname -m)"
runuser="$(whoami)"
trueuser="$(who am i | awk '{print $1}')" # if this is blank, we're actually root (kali)
# Edge cases... urgh. There *was* a reason it's like this. It'll get tested further
# later and get cleaned up as required in a later patch.
if [ "$runuser" == "root" ] && [ "$trueuser" == "" ]; then
  trueuser="root"
fi
if [ "$trueuser" != "root" ]; then
  userhomedir=$(echo /home/${trueuser})
else
  userhomedir=$HOME
fi
userprimarygroup="$(id -Gn "${trueuser}" | awk '{print $1}')"
rootdir=$(cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd)
silent=false
os="$(awk -F '=' '/^ID=/ {print $2}' /etc/os-release 2>&-)"
version=$(awk -F '=' '/^VERSION_ID=/ {print $2}' /etc/os-release 2>&-)
arg=""
BOLD="\033[01;01m"     # Highlight
RED="\033[01;31m"      # Issues/Errors
GREEN="\033[01;32m"    # Success
YELLOW="\033[01;33m"   # Warnings/Information
RESET="\033[00m"       # Normal

########################################################################
# Title Function
func_title(){
  # Echo Title
  echo '=========================================================================='
  echo ' ByWaf (Setup Script) | [Updated]: 17/06/2016'
  echo '=========================================================================='
  echo ' [Web]:  | [Twitter]: '
  echo '=========================================================================='
  echo -e '\n'
  #echo -e "Debug:      userhomedir = ${HOME}"
  #echo -e "Debug:          rootdir = ${rootdir}"
  #echo -e "Debug:         trueuser = ${trueuser}"
  #echo -e "Debug: userprimarygroup = ${userprimarygroup}"
  #echo -e "Debug:               os = ${os}"
  #echo -e "Debug:          version = ${version}"
}

# Environment Checks
func_check_env(){
  # Check Sudo Dependency
  which sudo >/dev/null 2>&-
  if [ "$?" -ne "0" ]; then
    echo ''
    echo -e ${RED}' [ERROR]: This Setup Script Requires sudo!'${RESET}
    echo '          Please Install and Configure sudo Then Run This Setup Again.'
    echo '          Example: For Debian/Ubuntu: apt-get -y install sudo'
    echo '                   For Fedora 22+: dnf -y install sudo'
    exit 1
  fi

  # Double Check Install
  if [ "${silent}" != "true" ]; then
    if [ ${os} != "kali" ] || [ "${os}" == "parrot" ]; then
      echo -e "${BOLD} [!] NON-KALI Users: Before you begin the install, make sure that you have"
      echo -e "     rest of the components installed before you proceed!\n${RESET}"
    fi
    echo -e ${BOLD}'\n [?] Are you sure you wish to install ByWaf?\n'${RESET}
    read -p ' Continue With Installation? ([y]es/[s]ilent/[N]o): ' installveil
    if [ "${installveil}" == 's' ]; then
      silent=true
    elif [ "${installveil}" != 'y' ]; then
      echo -e ${RED}'\n [ERROR]: Installation Aborted By User.\n'${RESET}
      exit 1
    fi
  fi

  func_package_deps

  # Finally, Update The Config
  if [ -f "/etc/bywaf/settings.py" ] && [ -d "${outputfolder}" ]; then
    echo -e ${YELLOW}'\n\n [*] Setttings already detected... Skipping...'${RESET}
  else
    func_update_config
  fi
}

# Install Architecture Dependent Dependencies
func_package_deps(){
  echo -e "\n\n [*] ${YELLOW}Initializing Package Installation${RESET}"

  # Start Dependency Install
  echo -e ${YELLOW}'\n\n [*] Installing Dependencies'${RESET}
  if [ "${os}" == "ubuntu" ] || [ "${os}" == "debian" ] || [ "${os}" == "kali" ] || [ "${os}" == "parrot" ]; then

    # Install requests for python2 using pip.
    sudo pip install requests
  fi
}


# Update ByWaf Config
func_update_config(){
  echo -e "\n [*] ${YELLOW}Updating ByWaf Configuration...${RESET}"
  cd "${rootdir}/config/"
  echo -e "\n ${rootdir}/config/ \n"

  # SUDOINCEPTION! (There is method behind the, at first glance, madness)
  # The SUDO_USER environment variable of the actual user doesn't get passed on to the python interpreter properly,
  # so when we call "sudo python update.py", it thinks the user calling it, it's interpretation of SUDO_USER is root,
  # and that's not what we want. Look at this fake process tree with what the env variables would be...
  #    - |_ sudo setup.sh ($USER=root $SUDO_USER=yourname)
  #      - | sudo -u yourname sudo python update.py ($USER=root $SUDO_USER=yourname)
  # snip 8<-  -  -  -  -  -  -  -  -  -  -  -  -  - The alternative below without "sudo -u username"...
  #      - | sudo python update.py ($USER=root $SUDO_USER=root)
  # snip 8<-  -  -  -  -  -  -  -  -  -  -  -  -  - And thus it would have screwed up the $WINEPREFIX dir for the user.
  if [ -f /etc/bywaf/settings.py ]; then
    echo -e " [*] ${YELLOW}Detected current ByWaf Framework settings file. Removing...${RESET}"
    rm /etc/bywaf/settings.py
  fi
  sudo -u ${trueuser} sudo python2 update.py
  

  # Ensure that user completely owns the wine directory
  if [ -f /etc/bywaf/settings.py ]; then
    echo -e " [*] ${GREEN}Settings file completed. Returning...${RESET}"
  fi
}

########################################################################


# Print Banner
func_title

# Check Architecture
if [ "${arch}" != "x86" ] && [ "${arch}" != "i686" ] && [ "${arch}" != "x86_64" ]; then
  echo -e "${RED} [ERROR] Your architecture ${arch} is not supported!\n\n${RESET}"
  exit 1
fi

# Check OS
if [ "${os}" == "kali" ]; then
  echo -e " [I]${YELLOW} Kali Linux ${version} ${arch} Detected...${RESET}\n"
elif [ "${os}" == "parrot" ]; then
  echo -e " [I]${YELLOW} Parrot Security ${version} ${arch} Detected...${RESET}\n"
elif [ "${os}" == "ubuntu" ]; then
  version=$(awk -F '["=]' '/^VERSION_ID=/ {print $3}' /etc/os-release 2>&- | cut -d'.' -f1)
  echo -e " [I] ${YELLOW}Ubuntu ${version} ${arch} Detected...${RESET}\n"
  if [[ "${version}" -lt "15" ]]; then
    echo -e "${RED} [ERROR]: Veil-Evasion Only Supported On Ubuntu 15.10+.\n${RESET}"
    exit 1
  fi
elif [ "${os}" == "debian" ]; then
  version=$(awk -F '["=]' '/^VERSION_ID=/ {print $3}' /etc/os-release 2>&- | cut -d'.' -f1)
  if [ ${version} -lt 8 ]; then
    echo -e " [ERROR]${red} Only Debian 8 (Jessie) and above are supported!\n"
    exit 1
  fi
elif [ "${os}" == "fedora" ]; then
  echo "${YELLOW} [I] Fedora ${version} ${arch} detected...\n${RESET}"
  if [[ "${version}" -lt "22" ]]; then
    echo -e "${RED} [ERROR]: ByWaf only supported on Fedora 22+.\n${RESET}"
    exit 1
  fi
else
  os=$(awk -F '["=]' '/^ID=/ {print $2}' /etc/os-release 2>&- | cut -d'.' -f1)
  if [ ${os} == "arch" ]; then
    echo -e " [I] ${YELLOW}Arch Linux ${arch} detected...\n${RESET}"
  elif [ ${os} == "debian" ]; then
    echo -e " [!] ${RED}Debian Linux sid/TESTING ${arch} *possibly* detected..."
    echo - "      If you are not currently running Debian Testing, you should exit this installer!\n${RESET}"
  else
    echo -e " [!] ${RED}Unable to determine OS information. Exiting...\n${RESET}"
    exit 1
  fi
fi


# Menu Case Statement
case $1 in
  # Make Sure Not To Nag The User
  -s|--silent)
  silent=true
  func_check_env
  ;;

  # Force Clean Install Of Python Dependencies
  # Bypass Environment Checks (func_check_env) To Force Install Dependencies
  -c|--clean)
  func_package_deps
  func_update_config
  ;;

  # Print Help Menu
  -h|--help)
  echo ''
  echo "  [Usage]....: ${0} [OPTIONAL]"
  echo '  [Optional].:'
  echo '               -c|--clean    = Force Clean Install Of Any Dependencies'
  echo '               -s|--silent   = Automates the installation'
  echo '               -h|--help     = Show This Help Menu'
  echo ''
  exit 0
  ;;

  # Run Standard Setup
  "")
  func_check_env
  ;;

*)
  echo -e "\n\n [ERROR] Unknown Option: $1"
  exit 1
  ;;
esac

file=$(dirname "$(readlink -f "$0")")"/setup.sh"
echo -e "\n [I] If you have any errors running ByWaf, contact us."
echo -e "\n [I] ${GREEN}Done!${RESET}"
exit 0
