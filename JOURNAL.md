# Learning Journal

- Prompt (what we're asking of our assistant): Read @/prompts/1-web-api-specs.md and follow the instructions at the top of the file.
- Tool (our AI assistant): Cline
- Mode (plan, act, etc.): Plan
- Context (clean, from previous, etc.): Clean
- Model (LLM model and version): Claude 3 Haiku 20240307
- Input (file added to the prompt): prompts/1-web-api-specs.md
- Output (file that contains the response): prompts/2-web-api-prompt.md
- Cost (total cost of the full run): $0.0064
- Reflections (narrative assessments of the response): My assisstant misunderstood the task. There was no prompt to speak of, straight to a plan for implementing. uwickly fixed when prompted. The resulting prompt looks a bit skinny on details, i.e. the exact tech stack details are missing - already in the context?

- Prompt: Read @/prompts/2-web-api-prompt.md and follow the instructions at the top of the file.
- Mode: Plan
- Context: Clean
- Input: prompts/2-web-api-specs.md
- Output: prompts/3-web-api-plan.md
- Cost (total cost of the full run): $0.0142
- Reflections (narrative assessments of the response): My assisstant misunderstood the task. There was no plan this time, i did get a propmt though. Easily fixed once prompted. Plan looks ok.

Prompt:  Please create a Config API Service in the `config-service` folder, according to the Implementation Plan defined in @/prompts/3-create-web-api-plan.md
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet Haiku 20250514
- Input: prompts/3-web-api-plan.md
- Output: config-service/
- Cost: $1.7098
- Reflections: Assistant didn't create tests, also the service wouldn't run once created. Lots of fixing todo.

Prompt:  There are no tests, please review and create
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Output: _test.py for each major codefile
- Cost: $2.2840
- Reflections: All major code files seem to have test, tests fiale dtghough due to pydantic validation errors. Also a bunch of deprecation warnings for pydantic serializers too.

Prompt:  Let's get the tests discovered correctly in VSCode and passing
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $1.0209
- Reflections: FIxed the test discovery in VSCode. Whilst my assistant fixed soem tests, not all are passing.

Prompt: Get all tests to pass
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $2.3670
- Reflections: The tests are all passing but the intial quality fo the solution meant taht the config, set up and soem basic taggign of reutes all made it really complicated fior my assisstant to find and fix the problems. It wasa costly exercise - maybe try and keep the scope smaller in future?

Prompt: Let's use docker for the database runtime for this project. create a docker compose file that sets up postgresql
- Mode: Plan
- Context: Clean
- Model: Claude 3.5 Haiku 20241022
- Cost: $
- Reflections: Worked really well.

Prompt: lets move the compose file to the config-service folder, move the README and gitignore files to the root folder and move and combine the .env file into the config-service folder.
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.2120
- Reflections: Worked really well - though it seemed like a lot of api calls.

Prompt: app has error when trying to run it
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.3506
- Reflections: Assistant fixed up the migrations and got teh app working. Looks like it deleted some criticla enviroenmtn variables as part of the exercise too.

Prompt: app has error when trying to run it
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.3506
- Reflections: Assistant fixed up the migrations and got teh app working. Looks like it deleted some criticla enviroenmtn variables as part of the exercise too.

Prompt: Lets align docker compose envrionenmnt variable naming with the format in teh .env file, i.e. DATABASE_DB as opposed to POSTGRES_DB. Also add defautl values.
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.2198
- Reflections: Worked really well.

Prompt: lets focus on applications. create an integration test for the create application flow. make sure to test the application exists after creation
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $2.2105
- Reflections: Lots of work, seemed to create a test, work with it an drealise that is t had brokena bunch of other tests. Fixed those first then created workign intergation tests based on that learning. Expensive and long, drawn out but got there in the end.

Prompt: when i test the api and the databse using the docker compose file, i can create an application but when i query for teh same application id i get: INFO:     127.0.0.1:59259 - "GET /api/v1/applications/01K4GGEZJ3MPNN12XD1BY1QVB3 HTTP/1.1" 404 Not Found
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.5759
- Reflections: Did a reqally good job of testing the applciation 'manually', post and getting from teh api to make sure all flows worked correctly.

Prompt: lets focus on configurations. create an integration test for the create configuration flow. make sure to test the configuration exists after creation
- Mode: Act
- Context: Clean
- Model: Claude 4 Sonnet 20250514
- Cost: $0.4960
- Reflections: Worked really well.

Prompt: Read @/prompts/4-admin-ui-prompt.md and follow the instructions at the top of the file.
- Tool: Cline
- Mode: Plan
- Context: Clean
- Model: Claude 3.7 Sonnet
- Input: prompts/4-admin-ui-prompt.md
- Output: prompts/5-admin-ui-plan.md

- Prompt: Read @/prompts/5-admin-ui-plan.md and follow the instructions at the top of the file.
- Tool: Cline
- Mode: Act
- Context: Clean
- Model: Claude Sonnet 4
- Cost: $2.2415
- Input: prompts/5-admin-ui-plan.md
- Output: ui/

- Prompt: the ui runs but shows nothing. please fix and make sure all test run
- Tool: Cline
- Mode: Act
- Context: Clean
- Model: Claude Sonnet 4
- Cost: $1.6705
- Input: prompts/5-admin-ui-plan.md
- Reflections: lots of work to fix imports and set up additioanl test mocks. e2e still not running due to `npm playright install` not being run. also ui doesnt seem to work for basci acreate application flow.

- Prompt: ui loads ok, shows internal server error and doesnet work when adding an aplication.
- Tool: Cline
- Mode: Act
- Context: Clean
- Model: Claude Sonnet 4
- Cost: $0.8938
- Reflections: Lots of examinations... took ages and went through a lot of stuff but worked out in the end.



