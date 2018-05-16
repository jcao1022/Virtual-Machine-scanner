import re
str = """
	   PREMAutoTest       :     Premises Development Automation Test
	   access             :     E7 Automation Test
	   aqa                :     
	*  barista            :     Barista, the Cafe Package Manager
	*  cafe               :     Cafe Core: Calix Automation Framework & Environment
	   cafe_abacus        :     abacus env setup.
	   cafe_ride          :     Installer for RIDE (the Robot Framework IDE) and its Plugin
	   ctrdb              :     CTRDB: Calix Test Result Database
	   dpu_mdu_automation :     G.Fast DPU/MDU Test Case Automation Suite
	*  hltapi_env         :     Traffic Generator HLTAPI env setup.
	*  red-ide            :     RED: The Robot Framework IDE
	*  ride               :     Installer for RIDE, the Robot Framework IDE
	   stp                :     System Test Premise Common Test Cases and Test Suites
	   stp_tools          :     [Processing Description...]
	*  winexe             :     Winexe, the Windows Shell

* - Package is installed on system.

"""

m = re.search("\*\s\s\w+", str, re.M|re.I).groups()
print m
