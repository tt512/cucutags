@testplan_6306
Feature: Empathy basics

# Works probably only in the Gnome3 Classic mode
#
#  @testcase_175167
#  Scenario: Close via application menu
#    * Make sure that Empathy is running
#    * Click to the Empathy on gnome-panel
#    * Click Quit
#    Then Empathy should quit correctly

  @testcase_172128
  Scenario: Exit using menu
    * Make sure that Empathy is running
    * I open GApplication menu
    * I click menu "Quit" in GApplication menu
    Then empathy shouldn't be running anymore

  @testcase_172129
  Scenario: Exit using shortcut
    * Make sure that Empathy is running
    * Press "<Control>Q"
    Then Empathy shouldn't be running anymore

  @testcase_172130
  Scenario: Start using Activities
    * Start Empathy via menu
    Then Empathy should start
