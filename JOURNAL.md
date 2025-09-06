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