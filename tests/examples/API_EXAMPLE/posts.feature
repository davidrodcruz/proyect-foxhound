Feature: Posts API on JSONPlaceholder

  @smoke @api
  Scenario: Get all posts
    Given the "user" makes a "GET" request to "jsonplaceholder" API to get all "posts"
    Then the response status should be 200
    And the response should contain a list of posts

  @api
  Scenario: Get post by ID
    Given the "user" makes a "GET" request to "jsonplaceholder" API to get "posts" with id "1"
    Then the response status should be 200
    And the response should contain a post with title

  @api
  Scenario: Create new post
    Given the "user" makes a "POST" request to "jsonplaceholder" API to create "posts"
    And the request body contains:
      | title     | body           | userId |
      | Test Post | Test content   | 1      |
    Then the response status should be 201
