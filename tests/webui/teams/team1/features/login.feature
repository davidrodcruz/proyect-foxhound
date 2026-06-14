@team1 @webui
Feature: Login on SauceDemo

  Background:
    Given the user is on the login page

  @smoke @ui
  Scenario: Successful login
    When the user enters username "standard_user" and password "secret_sauce"
    And the user clicks the login button
    Then the user should see the inventory page

  @ui
  Scenario: Invalid login shows error
    When the user enters username "invalid_user" and password "wrong_password"
    And the user clicks the login button
    Then the user should see an error message "Epic sadface"
