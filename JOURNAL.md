# Learning Journal

## Entry 1

- **Prompt** (what we’re asking of our assistant): Read @/prompts/1-web-api-specs.md and follow the instructions at the top of the file.
- **Tool** (our AI assistant): Cline
- **Mode** (plan, act, etc.): Plan
- **Context** (clean, from previous, etc.): Clean
- **Model** (LLM model and version): Claude 3 Haiku 20240307
- **Input** (file added to the prompt): prompts/1-web-api-specs.md
- **Output** (file that contains the response): prompts/2-web-api-prompt.md
- **Cost** (total cost of the full run): $0.0064
- **Reflections** (narrative assessments of the response): My assistant misunderstood the task. There was no prompt to speak of, straight to a plan for implementing. Quickly fixed when prompted. The resulting prompt looks a bit skinny on details, i.e. the exact tech stack details are missing - already in the context?

## Entry 2

- **Prompt**: Read @/prompts/2-web-api-prompt.md and follow the instructions at the top of the file.
- **Mode**: Plan
- **Context**: Clean
- **Input**: prompts/2-web-api-specs.md
- **Output**: prompts/3-web-api-plan.md
- **Cost** (total cost of the full run): $0.0142
- **Reflections** (narrative assessments of the response): My assistant misunderstood the task. There was no plan this time, I did get a prompt though. Easily fixed once prompted. Plan looks ok.

## Entry 3

- **Prompt**: Please create a Config API Service in the `config-service` folder, according to the Implementation Plan defined in @/prompts/3-create-web-api-plan.md
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet Haiku 20250514
- **Input**: prompts/3-web-api-plan.md
- **Output**: config-service/
- **Cost**: $1.7098
- **Reflections**: Assistant didn’t create tests, also the service wouldn’t run once created. Lots of fixing to do.

## Entry 4

- **Prompt**: There are no tests, please review and create
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Output**: _test.py for each major code file
- **Cost**: $2.2840
- **Reflections**: All major code files seem to have tests, tests failed though due to Pydantic validation errors. Also a bunch of deprecation warnings for Pydantic serializers too.

## Entry 5

- **Prompt**: Let’s get the tests discovered correctly in VSCode and passing
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $1.0209
- **Reflections**: Fixed the test discovery in VSCode. Whilst my assistant fixed some tests, not all are passing.

## Entry 6

- **Prompt**: Get all tests to pass
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $2.3670
- **Reflections**: The tests are all passing but the initial quality of the solution meant that the config, setup and some basic tagging of routes all made it really complicated for my assistant to find and fix the problems. It was a costly exercise - maybe try and keep the scope smaller in future?

## Entry 7

- **Prompt**: Let’s use docker for the database runtime for this project. Create a docker compose file that sets up PostgreSQL
- **Mode**: Plan
- **Context**: Clean
- **Model**: Claude 3.5 Haiku 20241022
- **Cost**: $
- **Reflections**: Worked really well.

## Entry 8

- **Prompt**: Let’s move the compose file to the config-service folder, move the README and gitignore files to the root folder and move and combine the .env file into the config-service folder.
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $0.2120
- **Reflections**: Worked really well - though it seemed like a lot of API calls.

## Entry 9

- **Prompt**: App has error when trying to run it
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $0.3506
- **Reflections**: Assistant fixed up the migrations and got the app working. Looks like it deleted some critical environment variables as part of the exercise too.

## Entry 10

- **Prompt**: Let’s align docker compose environment variable naming with the format in the .env file, i.e. DATABASE_DB as opposed to POSTGRES_DB. Also add default values.
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $0.2198
- **Reflections**: Worked really well.

## Entry 11

- **Prompt**: Let’s focus on applications. Create an integration test for the create application flow. Make sure to test the application exists after creation
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $2.2105
- **Reflections**: Lots of work, seemed to create a test, work with it and realize that it had broken a bunch of other tests. Fixed those first then created working integration tests based on that learning. Expensive and long, drawn out but got there in the end.

## Entry 12

- **Prompt**: When I test the API and the database using the docker compose file, I can create an application but when I query for the same application ID I get: INFO:     127.0.0.1:59259 - “GET /api/v1/applications/01K4GGEZJ3MPNN12XD1BY1QVB3 HTTP/1.1” 404 Not Found
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $0.5759
- **Reflections**: Did a really good job of testing the application ‘manually’, post and getting from the API to make sure all flows worked correctly.

## Entry 13

- **Prompt**: Let’s focus on configurations. Create an integration test for the create configuration flow. Make sure to test the configuration exists after creation
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude 4 Sonnet 20250514
- **Cost**: $0.4960
- **Reflections**: Worked really well.

## Entry 14

- **Prompt**: Read @/prompts/4-admin-ui-prompt.md and follow the instructions at the top of the file.
- **Tool**: Cline
- **Mode**: Plan
- **Context**: Clean
- **Model**: Claude 3.7 Sonnet
- **Input**: prompts/4-admin-ui-prompt.md
- **Output**: prompts/5-admin-ui-plan.md

## Entry 15

- **Prompt**: Read @/prompts/5-admin-ui-plan.md and follow the instructions at the top of the file.
- **Tool**: Cline
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude Sonnet 4
- **Cost**: $2.2415
- **Input**: prompts/5-admin-ui-plan.md
- **Output**: ui/

## Entry 16

- **Prompt**: The UI runs but shows nothing. Please fix and make sure all tests run
- **Tool**: Cline
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude Sonnet 4
- **Cost**: $1.6705
- **Input**: prompts/5-admin-ui-plan.md
- **Reflections**: Lots of work to fix imports and set up additional test mocks. E2E still not running due to `npm playwright install` not being run. Also UI doesn’t seem to work for basic create application flow.

## Entry 17

- **Prompt**: UI loads ok, shows internal server error and doesn’t work when adding an application.
- **Tool**: Cline
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude Sonnet 4
- **Cost**: $0.8938
- **Reflections**: Lots of examinations… took ages and went through a lot of stuff but worked out in the end.

## Entry 18

- **Prompt**: Let’s focus on the configurations area. When I add a new config it says it already exists, even when it doesn’t
- **Tool**: Cline
- **Mode**: Act
- **Context**: Clean
- **Model**: Claude Sonnet 4
- **Cost**: $1.7989
- **Reflections**: Lots of examinations… took ages and went through a lot of stuff but worked out in the end. Included thorough testing to validate the issue was fixed.