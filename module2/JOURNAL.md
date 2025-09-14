# Learning Journal - Module 2

## Entry 1

- **Prompt** (what we’re asking of our assistant): read thoruhg the file @/memory/ABOUT.md undersatdn teh structure and using your knowledge of the condiguration servuce application, create entries for each heading. Do not remove any of these headings. The file will form part of my memory so I can easily rememebr all the things and make more infored choices when refactoring/adding ne features. Create a plan outlinign what you will do to update it.
- **Tool** (our AI assistant): Cline
- **Mode** (plan, act, etc.): Plan
- **Context** (clean, from previous, etc.): Clean
- **Model** (LLM model and version): Claude 3 Haiku 20240307
- **Cost** (total cost of the full run): $0.1862
- **Reflections** (narrative assessments of the response): Interesting to see the files that my assistant selected to ghet the best overview of the aolution - assumed it to be based on the titles in the ABOUT.md file, i.e. how will I find the Object Model for Configuration. Detailed plan for completing the file.

## Entry 2

- **Prompt** (what we’re asking of our assistant): Execute the plan
- **Tool** (our AI assistant): Cline
- **Mode** (plan, act, etc.): act
- **Context** (clean, from previous, etc.): from previous
- **Model** (LLM model and version): Claude sonnet 4 20250514
- **Input** (file added to the prompt): @/memory/ABOUT.md (titles only)
- **Output** (file that contains the response): @/memory/ABOUT.md (completed)
- **Cost** (total cost of the full run): $0.1147
- **Reflections** (narrative assessments of the response): Detailed information in the ABOUT.md file that comprehensivley descrobes the Configuration Service. Trivial for my assistant - just followed the plan ;)

## Entry 3

- **Prompt**: You are an experienced system architect specialising in analysisng existing systems, idnetifying the key aspects from an archietcture perspectuve and producing comrehensive, refined context files that can be used by ai assistants. Read the file @/memory/ABOUT.md to get an idea of the application. Create a plan for producing a new context document @/memory/ARCHITECTURE.md. Fill it with the key archietcture insights. Make sure to inlcude, a breakdown of core componenets, including an overview, key patterns, key technical decisions, how errors are nadled, testing considerations/startegies, data requriements, endpoints exposed, etc... Ideally we will also have a C4 diagram of the system at a level 0 and level 1 altitude. Use mermaid format for the diagramming.
- **Tool**: Cline
- **Mode**: Plan
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Input**: @/memory/ABOUT.md
- **Cost**: $0.1140
- **Reflections**: Lots of questions from my assistant this time. Gave me the feeling that I was either too vague or that the stated role was craeting some demand for a more detailed understanding before creatign a plan. Plan looked solid enough, did have to prompt on a couple of things like data and/or storage strategy, actaul endpoint listing,e tc... taht were misse din the intial plan.

## Entry 4

- **Prompt**: Execute the plan
- **Tool**: Cline
- **Mode**: act
- **Context**: from previous
- **Model**: Claude sonnet 4 20250514
- **Input**: @/memory/ABOUT.md
- **Output**: @/memory/ARCHITECTURE.md
- **Cost**: $0.2154
- **Reflections**: Worked as requested... I did find myself thinking about iterating on the outptu for several items. Overall a good exercise, though I can see how a more detaield reqeust and proposed arch doc structure would have been beneficial from the get go.

## Entry 5

- **Prompt**: We're creating a context management system for ai assistants using cline. Plan a context overview docuemnrt taht describes te system and teh various aspects of needing to read teh memoery files beofre doign anything else, etc... use your underatding of memory-bank capabilities to create a comprehensive overview document.
- **Tool**: Cline
- **Mode**: act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $0.22478
- **Reflections**: Very similar context to the example file, my assistant seems to know teh concept fairly well ;)

## Entry 6

- **Prompt**: Using the following files, create a context document covering the technical implementation/details for the solution. use only the file paths provided and whatever context you already have from memory. Produce a plan for a new context file @/memory/TECHNICAL.md be sure to cover bopth the back end, front end and database. 

    Overview:

    - config-service/README.md

    Data Models:

    - config-service/svc/models/application.py
    - config-service/svc/models/configuration.py
    - config-service/svc/models/base.py

    Database:

    - config-service/svc/database/connection.py
    - config-service/svc/database/migrations.py
    - config-service/svc/database/migrations/002_create_applications_table.sql
    - config-service/svc/database/migrations/003_create_configurations_table.sql

    Repositories:

    - config-service/svc/repositories/application_repository.py
    - config-service/svc/repositories/configuration_repository.py

    Services:

    - config-service/svc/services/application_service.py
    - config-service/svc/services/configuration_service.py

    API Layer:

    - config-service/svc/api/v1/applications.py
    - config-service/svc/api/v1/configurations.py

    Configuration:

    - config-service/svc/config/settings.py
    - config-service/svc/.env

    Frontend Services:

    - config-service/ui/src/services/api-service.ts
    - config-service/ui/src/services/application-service.ts

    Frontend Models:

    - config-service/ui/src/models/application.ts
    - config-service/ui/src/models/configuration.ts

    Build and Deployment:

    - config-service/svc/pyproject.toml
    - config-service/svc/docker-compose.yml
    - config-service/ui/package.json
    - config-service/ui/vite.config.ts
- **Tool**: Cline
- **Mode**: plan + act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $0.2865
- **Reflections**: Really interesting process, given only the files plus memory, my assistant seemd really eager to use other files it coudl see but was told not to leverage. Results were less than ideal... needed to prompt them to get extra stuff added. Got there in the end but it took more work. Assitant definitely felt more constrained.

## Entry 7

- **Prompt**: Let's check what you have in memory.
- **Tool**: Cline
- **Mode**: plan
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $0.0738
- **Reflections**: Memory Contents Summary provided reports that all 3 context files (ABOUT, ARCHITECTURE, TECHNICAL) are there. Response also had a pretty hefty overview of the context of the solution from several different viewpoints. Score!

## Entry 8

- **Prompt**: Lets add an entry to the memory.md file for the TECHNICAL.md file lets make it part of a new section 2. Option Files (Loaded when needed). Write a simpel logic statement in thsi section that allows the use of a key work phrase to load in the TECHNICAL.md file if it isn;t already loaded. This file is mandatory to read once loaded but is optionally loaded when the user enters the phrase `CODING UPDATE:`
- **Tool**: Cline
- **Mode**: act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $0.0558
- **Reflections**: When i asked about the goals of the project, the ABOUT and ARCHITECTURE memory files were loaded and the goals reported. When I they asked to read the .env file and started the prompt with CODING UPDATE: the TECHNICAL file was read before the request was attempted. Seemed to be 'a way' to optionally load based on some pseudo code. Felt a bit weird though, like maybe there's a more streamlined way of doing it.

## Entry 9

- **Prompt**: CODING UPDATE: Using only your memory, plan the introduction of a client library instead of consuming the API directly.
- **Tool**: Cline
- **Mode**: plan & act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $1.2726
- **Reflections**: More back and forth than i expected, the memory fiels got read and the client plan seemed to be produced base don that. Difficult to tell teh difference without trying without the memeory files as a comparisson.

## Entry 10

- **Prompt**: CODING UPDATE: lets plan the refactor to make the the admin ui to use the new service client
- **Tool**: Cline
- **Mode**: plan & act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $4.6421
- **Reflections**: The useual large scale refactroing execise with lots of oevr confidence. SOme problems with builds once my assistant was sconvinced it was done. A couple of targeted chats helped resolve it. I actually spent an additional 1hr chatting back and forth to fix bugs and get a series of integration tests refreshed - my assistant seemd to need a whole bunch of detailed planning assistance to get this sorted. Very interetsing to see how soemtimes a simple requets is nowhere near enough to get the job done.

## Entry 11

- **Prompt**: Create a plan for optionally loading the TECHNICAL and ARCHITECTURE files based on the request being targeted at technical changes to the solution. Lets differentiate between core and optional context specifc files i.e. core might inlcude ABOUT, where as context specfic would include TECHNICAL, etc... lets remove the CODING uPDATE trigger altogether.
- **Tool**: Cline
- **Mode**: plan & act
- **Context**: clean
- **Model**: Claude sonnet 4 20250514
- **Cost**: $1.0473
 **Reflections**: Interested to see how this works... my assistnat went into overdrive here with validation files, edge case ytesting of the context lodaing protocol and semantic matching of key words, etc...


## Entry 12

## Entry 13

## Entry 14

## Entry 15

## Entry 16

## Entry 17

## Entry 18
