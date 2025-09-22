# Integrate the learning experience with reflection

## 1. Were you able to get your assistant to behave properly during the transitions?

For the most part, yes. I found that with larger, more overwhelming changes across a growing codebase, my assistant would occasionally badger me to move on with statements like "the remaining test failures are trivial, recommend moving to the next stage and addressing these later."

## 2. Did your assistant continue to adhere to your directives in other parts of its memory?

Yes. There were occasions where it seemed that memory had been lost but on asking questions, my assistant could answer and describe aspects of the memory files without having to go and read them again.

## 3. What was a behavior that your assistant took a lot of work to get right?

Two things... Testing being the most obvious. I got lots of seemingly celebratory "I've completed the implementation (or modification) of the tests" only to find out that they hadn't actually been run!

The second thing is still a problem... when fixing things, my assistant seems to try to find the easiest route to fix. For example, when fixing an e2e UI test, my assistant would decide to refactor a large chunk of the backend service to make it work - not realising it was breaking already-tested backend functionality.

## 4. Were you able to successfully get your assistant to pick up where you left off (with an empty context window) with just "what's the next step?" or "what is our status?"

Yes. No problem here. Even after a laptop restart, there seemed to be no problem in finding out exactly where we were and having exactly the same suggestions as what was next.

### General Notes

- I opted to use a hand crafted process heacvily influencde by the example from last week
- I used CLaude code in the terminal as opposed to Cline this time.
- I spent far too much time in accept edits mode as opposed to plan mode - a lesson for next time
- I also opted to rebuild the same boring application configuration app - it went really well for a while and then the wheels came off and I spent quite a while in endless pikcy senior dev mode pointing our thign staht I didn't like.
- I suspect that similar specs from the last few weeks and too broad a focus are driving the entertaining debates I'm hav9ng with my assistant ;)

**Before the next time we meet, please post a link to your repo and your reflections to Discord.**