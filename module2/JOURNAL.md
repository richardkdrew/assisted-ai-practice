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

## Entry 6

## Entry 7

## Entry 8

## Entry 9

## Entry 10

## Entry 11

## Entry 12

## Entry 13

## Entry 14

## Entry 15

## Entry 16

## Entry 17

## Entry 18
