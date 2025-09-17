# Integrate Learning with Reflection

1. How did you find collaborating with your assistant on the context docs given it can read the implementation? Did you collaborate using different models?

Pretty good. My assistant seemed to understand the concept really well and over several attempts at setting up auto context loading, there were no real problems. The content of the context docs seemed to cover all-the-things pretty well. I did find myself wondering in subsequent tasks how much my assistant was gleaning from the context doc vs peeking at the implementation code. I did use a couple of different models but settled on mostly Sonnet 4 after some initial experiments and stayed there for the duration.

2. Did you ever end up with too much memory for your context window and necessary session lengths?

No, though I can see how this might be the case if my assistant was left to decide what was important for memory. During the second iteration of auto-loading context files based on the request submitted, my assistant created a number of files to explain the process, provide examples and test the protocol. For example:

- `@/memory/loading-examples.md`
- `@/memory/loading-validation.md`
- `@/memory/request-type-validation.md`
- `@/memory/usage-patterns.md`

My assistant does like to create lots of content ;)

3. How eager was your assistant? How much did you have to delete or ask them to remove? Did you try to mitigate this for similar tasks in the future? Did your mitigations work?

I saw a difference on the occasions where I was specific about only using a certain set of files or just what was in memory. My assistant still seemed eager but had loads of questions. In contrast there was a situation where we had created the client library and I boldly asked the assistant to plan (and at some point too early in the process) act on refactoring the Admin UI to use the new client library. My assistant was surprisingly confident and took to it... this triggered a chain reaction of broken tests, confusion around what needed testing, discovery of feature flows/paths that were not working, etc... Overall the result was eventually good and we found (and fixed) a great deal of bugs but it took an age and cost a couple of bucks that could have been saved by a more targeted, phased approach.

4. How reliable was your assistant at loading the context? Were you able to use reliably use command phrases?

I had a mixed experience tbh... One of the tests I had in place to be confident that my assistant was indeed loading memory was to have them say `[MEMORY BANK: ACTIVE]` or `[ADDITIONAL MEMORY BANK: ACTIVE]` as they loaded files. This worked really well during the initial testing when I was using `CODING UPDATE:` as a trigger phrase to get my assistant to load ARCHITECTURE and TECHNICAL context files. However, over time having to type the trigger phrase before every prompt/request got a little onerous. When I shifted to a more complicated auto detection memory loading protocol, my assistant seemed to remember to load files but forget to say `[MEMORY BANK: ACTIVE]` or `[ADDITIONAL MEMORY BANK: ACTIVE]`. At other times when the token window got long, it seemed like my assistant occasionally forgot to load the memory files all together.


Before the next time we meet, please post a link to your repo and your reflections to Discord.