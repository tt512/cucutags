Feature: Empathy App menu actions

    Background: Empathy Setup
        * Make sure that Empathy is running
        * I open GApplication menu

    @testcase_184264
    Scenario: Contact list - help contents
        * I click menu "Help" in GApplication menu
        Then Yelp should start

# 1. Choose 'application menu->Accounts'
# 2. In the 'Messaging and VoIP Accounts' click + to add a new account
# 3. Select 'Google Talk'
# 4. Put 'desktopqe@gmail.com' as a Google ID
# 5. Put 'redhatqe' as password
# 6. Check 'Remember Password'
# 7. Hit 'Apply'

#    @testcase_181366
#    Scenario: Add account - GTalk
#        * I click menu "Accounts" in GApplication menu
#    Then Account should successfully connect (be 'Available')
#
