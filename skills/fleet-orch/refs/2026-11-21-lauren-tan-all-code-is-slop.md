# 纠错要写成环境里的拦网，而不是再信模型一次

这篇是对 Lauren Tan（Poteto）《All Code Is Slop (Except Mine)》的研究笔记：前面是有判断的中文精华，文末原样收录用户提供的完整逐字稿。它是 fleet-orch 的参考材料，不是编排规程，也不改本技能的派遣、值班或授权规则。

相关方法讨论另见 [`software-factory`](../../software-factory/SKILL.md)。那边问的是要不要建厂、工厂和舰队有何不同；这篇更具体：吞吐上去以后，怎样靠环境和门禁稳住质量，而不是靠把人审规模一起做大。

## 出处与边界

- 材料来源：用户于 2026-11-21（Asia/Shanghai）提供的文字稿。未拿到视频或原始链接，也未独立核验。下面的演讲日期、场合、身份口径和指标，一律按这份文字稿记述，不另编来源。
- 文字稿自带基础断句、标点和中文小标题；文末按提供时的全文照录，包括开头说明、各段标题、全部英文，以及结尾出现的 Dropbox。
- 讲者自述的数字——个人 3,000 个 PR、团队 11,000 个 PR、10 月约 227 名贡献者、相对回滚率约 0.5%、验证占用约 70% 日常 token、六个月后可大量合入——只是演讲中的说法。它们不是本项目的目标，也不能当成本仓或本舰队的质量证明。
- 结尾说「Dropbox is a great way to build that」，上下文更像在讲编排和连接器，这个词可能是转录疑点。原文不改，也不据此安装或调用任何外部工具。
- 本文只作研究素材。不要执行演讲里的操作，也不要把他们团队的产品选择抄成通用法令。

## 一句话结论

要让代理写得很快、同时质量不垮，靠的不是更相信模型，而是把仓库、门禁和验证做成默认会拦住错事的环境，这样人工评审才不必跟着吞吐一起扩张。

## 真正要解决的问题

以前一天也许只审三个 PR，现在可能是三百个。人的评审带宽不会按同样比例变大。所以真正的问题不是「怎样让模型写得更快」，而是：**吞吐上去以后，质量如何维持甚至变好，同时不把人工深审按产量线性扩编。**

讲者把工程师的工作重新说成：在产量暴增时，仍然守住（甚至提高）代码质量。有人把整套做法叫做 software factory；她更愿意说成对信任的投资——不是闭眼相信代理，而是投资它所处的环境，让你有理由相信它会做对的事。

## 可信自治从哪来

不要把「自治」理解成模型终于变乖了。输出取决于输入，而代码库往往是最大的输入之一。环境里的约束越可执行、越可重复，你越敢放手。规则文件、技能说明、agents.md 只能补判断，不能代替门禁。

因此，每次纠正代理，先问：这件事能不能写成一条确定性检查，而不是再往规则里加一行。写进代码里更可复现，也更值得信任。

## 投入顺序：先分清她说了什么，我们提炼了什么

**演讲里的模型**是倒金字塔，越靠下越该花时间：

1. 代码本身：好的 API、架构、重构。
2. 静态门禁：linter、类型系统、编译器，以及各类测试。

这两层是确定性的，合在一起用来限制代理能做什么，并迫使它默认做对的事。

3. 再叠验证：把代码真正跑起来的检查，以及形式化方法，用来找 bug、核对你希望始终成立的性质，并判断代理是否理解了目标和意图。
4. 最后才是少量文字：规则、skills、agents.md，留给需要判断的事。

**我们的提炼：**这个顺序的要点不是「形式化越高越好」，而是越靠前的层越便宜、越可重复、越不依赖某次对话里的自觉。文字规则最好写、也最容易失效：代理会把一次小纠正理解成永不打破的硬规则，也会在注释和文档里给自己开脱，说明这次为何可以不按正确做法来。注释还会过时，人本来也不爱读，而且不可强制执行。所以「告诉下一个代理别这样做」如果只写在注释里，并不是你可以信任的东西。

## 把一次纠正变成能拦住同类问题的机制

通用原则是：每次纠正，都尽量变成确定性检查，或通过更好的 API 和架构，从根上取消整类问题。做的次数够了，评审时要盯的事项会变少。

同时要清理旧的坏样本。因为代码是最大输入，变通写法、反模式、过时代码和技术债看起来会像「项目里的既定做法」，下一个代理就会照抄。花园里的杂草会迅速蔓延。所以要先加门禁拦住新的反模式，再把仓库里旧的同样清掉。只拦增量、不清理存量，等于继续给代理提供坏教材。

演讲里的例子是 Grok Bot / Dune 的做法，不是通用戒律：他们把需要很多分寸才能用对、代理又经常用砸的 API（她举了 React 的 useEffect）在产品代码里禁用，只留在框架内部少数位置；用目录结构和依赖分析，禁止主线程与渲染线程互相引用；代理爱用 `setTimeout` 一类计时器打补丁、掩盖架构冲突，还写注释证明这个补丁合理，后来用 lint 明确要求修根因，而不是绕过去。他们还选择禁止产品代码里绝大多数注释。这些都是特定代码库里的工程选择。不要把「禁用 useEffect」或「禁止注释」当成所有项目都要遵守的硬规则。

## Feature map：用用户的话验收，并留下可重复的证据

他们的代码评审逐渐从读完每一行，收缩成看验证产物：录像、截图、图示、形式化结果。

最基本的一层，就是让代理自己把代码跑起来，并用人类开发者也会用的调试手段。运行时验证技能里有他们称为 feature map 的东西：从用户视角列出产品功能，相当于一张共用的功能地图。这样你说「左侧栏那个东西」时，代理不必靠猜。技能里还有可复用的命令行和 driver，每次都能重跑，既省 token，也可测试。真正有用的是两件事：验收的入口和用户的词汇对齐；收集证据的步骤可以重复，而不是每次重新发明。

形式化方法是再上一层，不是起步条件。文字稿里，他们用 TLA+ 检查跨设备通知等主流程，用 Lean 检查某些算法性质（例如自研虚拟化库有没有闪烁或抖动）。讲者自己说仍在实验，已经找到一些 bug，但不是银弹，只是环境里的又一层面。另有面向界面的基于性质的测试，也抓到过一些问题。

这里必须把边界说死：**验证只针对写进模型或性质里的东西。规格写错了，证明通过也不等于产品是对的。形式化证明更不等于真实界面没有 bug。** 线上表现、性能和观感，还得另外检验。验证可以帮助判断代理是否理解了意图，但不能代替去看真实使用结果。

## 对 fleet-orch 的具体含义

1. **并发不是质量保障。** 舰队的价值是同时跑多个工人，这只解决吞吐和值班，不自动提高质量。如果内层编码循环本身在产出劣质改动，再并行、再自动化，只是更快地制造更多同样的问题，还要砸更多 token。先把代码库、静态门禁和验证故事做强，再谈工厂和自动合并。很多验证工作本来就是自动化的前提。
2. **工人自证不足。** 本技能已有「通知是声称，不是真相」「先验证再汇报」。这篇材料把它说得更透：工人说 done、自己写的理由、自己写的注释，都不够。要看的是可重复的门禁结果和验证产物。Armstrong 模型里「评审项要带截图和演示」，和这里「评审收缩成看验证产物」，是同一方向。
3. **审查证据和门禁，而不是扩人去读每一行。** 老板的职责应逐渐从「读完工人改动的每一行」转向「确认门禁在、证据在、意图被核对过」。任务卡写清验证方法，receipt 带证据链接，而不是一段自述。
4. **按风险逐步提升自治。** 讲者描述，他们在基础足够好之后，多数产品代码不再需要深度人工评审，修复 PR 甚至会自动合并。这是她对 Grok Bot 现状的自述，不能当成 fleet-orch 的默认策略。本技能现行纪律仍是：先验证再汇报，不可逆操作要问，提交和推送需明确授权，生产写入要有门和备份。低风险、门禁完整、证据可复查的改动，可以减少重复深审；涉及生产、安全、权限或不可逆操作的，不能因为「别的团队在自动合并」就放开。

## 最小可落地闭环

不要一上来建工厂、上自动合并、上形式化验证。下次纠正工人时，按这个短闭环做：

1. 先改代码，或加一条能自动拦住的检查，而不是只写进规则或 receipt。
2. 用同一条检查清理仓库里已有的坏样本，避免代理继续抄。
3. 给任务准备可复用的验收入口：用户能听懂的功能名称（feature map 的思路）、能重复跑的命令或 driver、跑完留下的证据（测试输出、截图、录像、日志）。
4. 老板看这些证据和门禁，而不是工人的自我评分。
5. 只有当这类闭环已经能稳定拦住同类问题时，再考虑对更低风险的改动减少深审。形式化方法是可选加层，不是起步条件。

## 失效边界

- 禁用 useEffect、禁止注释、把约 70% token 花在验证上、约 0.5% 回滚率、自动合并：都是讲者团队在特定代码库、特定阶段的选择或自述，不是所有项目的硬规则。
- 自动合并在他们那里成立，前提是「代码库已经足够好，PR 默认往往是好的」。门禁不完整、旧坏样本还在、验证只能由作者自己说了算时，自动合并就是在加速事故。别处的工厂实践也有「工厂不合入、仍由人审批」的相反答案，不要混成一条教条。
- 形式化验证通过，不等于真实界面没 bug，不等于规格正确，也不等于线上结果可接受。
- 不要把演讲里的吞吐数字当成排期或质量目标。内层循环如果还在产出劣质改动，先自动化只会放大问题。

---

## 原文逐字稿

以下为用户于 2026-11-21（Asia/Shanghai）提供的完整文字稿，原样收录，未做删节或「校正」。

视频完整逐字稿如下，已经做了基础的断句和标点处理，方便阅读。
All Code Is Slop (Except Mine) — Lauren Tan (Poteto), SpaceX AI
[开场：主持人介绍]
Hundreds of pull requests a day and nobody reads them all. So how does code quality keep improving? To share how the Grok Bot team turns slop into gold, please welcome Lauren Tan, Principal Engineer at SpaceX Superintelligence.

[Lauren 登场]
Hello everyone. Don't know if you can see my slides. But my name is Poteto, also known as Lauren, and I'm very excited to chat with all of you today. Maybe you can get a big round of applause for our tech team, helping me with my laptop. Okay. I don't see it. Ah, there you go. All right. Um, so again, my name is Poteto. I work on Grok Bot at SpaceX AI.

[互动环节]
And can I just get a quick show of hands? How many of you have ever looked at code that somebody else wrote, and you thought, that's all slop? Well, I have too. But today I'm gonna convince you that you can turn that slop into gold.

[核心数据点]
And so I did something crazy last month, and I shipped 3,000 pull requests to production. Now before agents, we never really cared about volume, except for the outliers. And at my previous company, we called these people coding machines. People like Bret Taylor, who famously rewrote all of Google Maps in a weekend. Just an insanely productive engineer. And well, with agents, anyone can now be a coding machine.

[核心论点]
And my thesis is that the job of the software engineer, the meta of being a software engineer, is figuring out how to maintain or even improve the quality of your code while massively increasing your productivity. To get there, some people like to call this a software factory, but I like to keep it simple, and I think of it as all about trust. Not blind trust, but investing in your agent's environment, so you can trust that your agents are going to do the right thing. Now it takes quite a lot of effort to get there, and it took me six months to get to a point where I could ship thousands of pull requests, a lot of them in my sleep. But it's certainly possible, and it will take you much less time than I did.

—— 第一部分：从低信任到高信任 ——

[逆金字塔模型介绍]
So let's start by talking about how we move from a low trust environment to a high trust one. So this inverse pyramid is how I think about where to spend time on your agent's environment. The first two layers are deterministic. So using your code itself — so things like good API design, architecture, refactoring — or using linters, type systems, compilers, or you know, different kinds of testing. And you can use both of these layers together to constrain what agents can do and force them to do the right thing by default. Verification, both runtime and formal, are great tools to layer on to find bugs and check properties and the invariants in your system that you want to hold true. And also help you check whether or not the agent understood your goals and your intent. And then finally, you want to layer with a little bit of prose. So things like rules, skills, agents.md — things that require judgment.

[代码库是最大的输入]
But let's start with your code base. Agents generate their outputs based on their inputs. And so the quality of the input really matters. And it just so happens that your code base is one of the largest inputs. So whenever you're correcting your agent, think about how you can make that a deterministic check instead of adding another line to your rules or your agent's .md, because it's far more reproducible when it's in code and it lets you trust it more.

[花园比喻]
And the analogy that I like to use is that your code base is kind of like a garden. You know, code used to arrive a few pull requests at a time. And I remember going into work in 2024 and reviewing the three pull requests that my colleagues wrote. And today that number is more like three hundred. So, you know, every engineer is now a team of hundreds or even thousands of agents. And code is arriving so rapidly that it almost feels like a continuous stream, and it almost feels organic, like a living thing. And in this analogy, your code base, the constraints that you impose, the guardrails that you put up, are the concrete foundations that the new code that your agents write grow around, just like the building in this picture. And so in many ways, the job of being a software engineer is kind of becoming like gardening.

[技术债会被放大]
Because code is the biggest input for agents, it means that any workarounds, anti-patterns, deprecated code, tech debt — it's now likely to be just copied by the next agent since it looks like the established pattern in your code base. And it's like you have some weeds or pests growing in your garden, and then they spread everywhere before you know it. So you want to make your code base as pristine as possible, so that agents are always copying the good stuff.

—— 第二部分：具体实践案例 ——

[案例1：Dune框架]
All right, let's look at some real examples. So Dune is a client framework that we created for Grok Bot to implement this idea of organic architecture. It's not really that interesting technically. You can kind of think of Dune as kind of like Next.js for Electron apps. But the interesting part of Dune is that it has a lot of constraints and linters that we've encoded a lot of the lessons that we've learned building desktop applications. And one such lesson is that anything that requires nuance to use well often leads to slop. You know, your classic example is use effect in React, right? It has its use cases, but it's often misused. You know, some people joke that you need a PhD to use use effect. And in other words, it really requires a lot of nuance to use, and agents are not good at using it. So our solution has been to just ban it in product code, and it's really only allowed in some places inside of Dune APIs. And effectively, this problem has now been categorically eliminated, and we never need to catch that during code review again.

[案例2：目录结构约束]
Another interesting pattern that we use is context through directory structure. So one anti-pattern that we saw with Cursor, which is an Electron app, is that agents would often import main thread code into the render thread, which would cause long tasks and jank. So in Grok Bot and in Dune apps, we've made this very, very conventional. We have these two top-level directories, literally called "electron renderer" and "electron main." And imports between them are forbidden or banned by our dependency graph analyzer and some linters. And again, you know, these are simple rules to set up, but it means one less thing that we need to review and think about during code review.

[案例3：禁止注释]
And then one more surprising thing that I've seen is agents using markdown — so things like documentation, code comments, rules, or skills — and the users as a place to write down their justifications for not doing the right thing. Or I don't know if you've ever seen this, but they'll over-rotate on some small correction that you made, and they treat it like a hard rule that can never be broken ever again.

[案例4：Cursor的定时器问题]
And here's another example from Cursor. So agents really loved using imperative timers — so things like setTimeout, requestAnimationFrame, requestIdleCallback. And they were using these as quick fixes, because they were really patching over an architecture clash between VS Code's imperative style and React's declarative style. So our choice of architecture actually made both the client and agent performance much worse. And if you've ever done any performance work in JavaScript, you'll know that when you have tons of timers being rapidly created and destroyed, it causes a lot of major garbage collection, which causes a lot of lag and jank. But the worst part is that agents wrote a lot of code comments, like you can see in red here, explaining why this quick fix was justified. And before you know it, we had timers spreading everywhere, and the performance of the app really suffered.

[解决方案：Dune的做法]
Now in Grok Bot, we learned our lesson there, and we decided to just ban 99% of comments. Because they go stale easily, humans just really don't bother reading the comments anyway. And again, it gives an agent the escape hatch to justify not doing the right thing because it's hard. And the worst part about comments, though, is that they're not enforceable. So what seems well-intentioned — you know, like "I'm going to tell the next agent not to do something" — never ends up actually being anything that you can trust. So in Grok Bot and in Dune, we now have lint rules that give good and very helpful error messages telling the agent to fix the root cause, the real problem, rather than just patch around it.

[通用原则总结]
And so our general principle is that every time we correct our agents, it turns into one of these deterministic checks, or we think about how to categorically eliminate that problem in the code through better API design, through better architecture. And if you do this enough times, you'll find that you have just less things to look out for in code review. And at some point, you realize there's nothing left to review, and you can just let agents merge most of their own pull requests.

—— 第三部分：验证（Verification）——

[验证的重要性]
All right, moving on. Verification is also a really big part of how we make our agent more autonomous, and also increase our confidence and trust in their work. And our code review process has now really shrunk into looking at verification artifacts instead. So things like videos, screenshots, diagrams, formal verification.

[运行时验证]
And the most basic example of this is runtime verification, which is just a fancy way of saying giving your agent a way to run the code for itself. And use debugging tools that, you know, human developers use as well, like the Chrome DevTools Protocol. In our runtime verification skills, we have this thing that we call a feature map. And that's basically kind of like a sitemap of all of the features that are available in your application from the user's point of view. And so with this, agents don't need to guess when you say, you know, "the thingy in the left sidebar." It gives you some shared vocabulary. And we also make use of custom CLI lines inside these skills, so that agents can reuse the CLI and the driver every time, which cuts down on token usage and is also testable.

[形式化验证]
And then recently, we've also started looking at formal verification. So we now use TLA+ to do some model checking of major user flows, such as notifications across multiple devices and platforms. We use Lean as well for proving certain algorithms. For example, we have our own — we wrote our own custom virtualization library — and we use Lean there to check that we don't have, you know, flickering or jittering problems. And we're still experimenting with this approach. Overall, it seems very promising. We've already found quite a few bugs with formal verification. But it's certainly not a silver bullet, and we're treating it as another tool, another layer in our agent's environment.

[基于属性的测试]
And then — this is a very fast video — but another thing that we just started looking at is property-based testing as well for UIs. So we use this library called Bombadil, and this has also caught a few UI bugs for us already.

—— 第四部分：行业趋势与成果 ——

[Cindy 的推文与验证占比]
Okay, so zooming out. I saw this tweet from Cindy. And six months ago, she said that she was talking about not being able to trust her agents because of subtle bugs that were getting merged. And really, what was missing for her in being able to trust her agents was the verification process. And now six months later, she says that 70% of her daily tokens go into verification. And I'd say that that tracks with what I see as well — that most of my token usage goes to verification.

[验证工具不是新东西，但成本被AI降低了]
And if you really look closely at her process, none of these things here are new or novel techniques that we've never had before. These are just good software engineering tools, but ones that might have been prohibitively expensive to use before, as they were hard to understand or write or maintain. But agents drastically cut this cost down, and really, we are entering a golden age of software testing and verification. Because agents let us test everything to a much greater degree than used to be economical.

[形式化验证帮助理解意图]
And then formal verification can also help you better reason about how your product should work, and whether your agents really understand your intent and goals. I made this new skill called State Chart in my plugin — Poteto Stack — which helps you visualize state machines from the user's point of view. And I find this much easier to review alongside the videos and screenshots that we provide. And so that's been great. Sorry for the flash bang.

—— 第五部分：成果与建议 ——

[成果数据]
Ah, okay. Now let's look at what the promised land looks like — what do you get in return for all of this investment? So on the Grok Bot team, our velocity is taking off and rapidly increasing. And last month, our team shipped a ridiculous 11,000 pull requests to production, which is a wild number. And our pace of releasing the client has also increased, and we cut a new stable version about once a day. And then the core team is also shipping much more, and we also have a lot more casual or drive-by contributors who don't always have a lot of context, but they're also contributing. And in October, we had about 227 people who contributed at least one pull request.

[质量没有下降]
So despite this velocity accelerating, you might be thinking to yourself, like, isn't this going to be chaos? You know, isn't this going to be a bunch of slop? But actually, the number of PRs that get reverted has actually gotten lower on a relative basis, and is steady at about half a percent. But I think the really interesting thing about this shipping pace and this volume of pull requests is that the performance of Grok Bot has stayed not just stable, but has improved on multiple dimensions compared to when we launched. So startup, typing, opening new chats, switching chats — all of this has gotten faster. And keep in mind, Grok Bot is still an Electron app, for now, so there is a ceiling, right? But it's already much faster than many other agent UIs out there. And for an Electron app with this high velocity and this many people contributing, I'd say that's pretty good.

[给听众的建议]
So before you jump into building out a software factory and automating everything that you can, whenever you correct your agent, try and do it by improving your code base first. You know, start with a lint rule to prevent new occurrences of anti-patterns, and then clean up those old patterns as well. And then make sure that your verification story is really strong. A lot of this work is a prerequisite to automation anyway. And if your inner coding loop produces slop, then automating that loop just produces more slop, and you need to throw more and more tokens at the problem, which we all know is very expensive. And once you make these investments into your code base — static analysis, runtime, formal verification — you'll start to find that many things become possible with these foundations, and that you can really easily build your own factory on top of these foundations.

[结尾：Dropbox工具 + 总结]
And when you're ready, Dropbox is a great way to build that. We have tons of connectors, routines that can kick off Cursor cloud agents and projects, which let you orchestrate hundreds or even thousands of agents. And as a quick example, you know, whenever we cut a new release, now Grok Bot will automatically spin up a new Cursor project first that will fuzz the entire application, the entire build, and it will find bugs by running the app and using it like a real user. And then it's going to open fix PRs for each of those bugs that it finds, and it's going to auto-merge — as crazy as that sounds. And that's because our code base is good enough that pull requests tend to just be good by default, and most product code that we land no longer really requires deep human review. So when you have solid foundations and good organic architecture, you can turn slop into gold. And you can ship with high quality, high velocity, without compromising on quality. My name is Poteto, also known as Lauren. Thanks again for listening to my talk.
