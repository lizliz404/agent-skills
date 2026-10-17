# Idea: browser-only Screen Studio-style recorder (Liz, 2026-10-18, verbatim)

Recorded verbatim from Liz; not edited, translated or corrected. This idea will become a separate repo; it lives here for now because it grew out of the talkcut work.

---

再之后，我想聊另外一件事。今天我一开始是在研究 Linux 上面有什么比较好的类似 Screen Studio 的录屏。一开始是找到了 Recorderly 的 Linux 版本，然后还有一个叫 Screenix 这个产品我感受起来哈，我还没体验。但事实上我觉得壁垒一点都不大，我觉得完全花一个小时自己重新做一个都不是问题，所以我就没打算付费。我反而是 Reboot 到 Windows 那边，然后去用了一下 Windows 版的 Recorderly。因为 Windows 上的这种视频录屏工具生态也很烂，几乎没有合适的。然后我就继续用了 Recorderly。其实使用体验呢，也没有多好。首先是那个整个弹窗很垃圾。再之后使用起来也是卡卡的。我不知道是我机器的问题，还是它这个电脑的问题，又或者是 Windows 自己的问题，又或者是确实屏幕快不行了。但我当前就是没问题啊，我回 Linux 这边时候就是没问题啊。所以我觉得可能是 Windows 它自己出了点小问题吧。

然后换来换去我觉得也麻烦。而且之后我长期上传视频啊、剪视频啊，除非我确实是要用剪映，但是剪映我现在都用的少了，我发现用 AI 剪视频快的多。所以说我之后也会尽量的用 AI 剪视频。那你如果用 AI 剪视频的话，那肯定要用 Linux 呀，因为 Linux 这边的 Agent 就是更好用啊，Windows 那边的 Agent 我今天又用了几分钟，我就感觉他妈的太难用了，PowerShell 真的一大堆毛病。不仅仅是 PowerShell 原本就很难用，再其次就是我最近好像还把它搞坏了。说什么 shell 损毁。

当然，这是我的这一个 specific case，所以说没那么重要，算是 edge case。我这里想强调的就是，Windows 的这种类似 Screen Studio 的生态很烂，然后 Linux 也差不多。然后我就想着说，我们有没有可能做一个只在浏览器中发生的呢？完全可行啊。 

https://www.excalicord.com/

https://github.com/goking81/excalicord-plus

只不过他这种做的是 3:4 的，对吧？按照他这种方法，做那种它特定形式的这种 3:4 的视频可能就非常快，然后后面配一个类似 Xkcd、 Xkcdro 的白板，再合适不过。这是另外一种方式，但是这种视频其实我们现在做的比较少，我自己现在做的比较少。然后我就想着能不能把那种 Screen Studio 最典型的几个特性塞到浏览器里面呢？那之后就不需要处理这么多复杂度了，你懂我意思吗？

你原本要处理什么复杂度？比如说这个屏幕，他妈的，你得要确定当前 captured 的是哪个屏幕，而是屏幕一还是浏览器，还是那个 terminal 等等之类的，就很烦。然后之后完全外包了，就相当于是你的麦克风请求，然后 integrated camera 的请求都包给了浏览器，然后它拿到这个权限之后就可以开工了。只是说我现在不确定是做成一个插件形式还是什么形式。而且市面上有没有重复的轮子呢？我觉得肯定是有相应需求和赛道的。意思就是说，在浏览器各个页面之间，你可以各页面切换哈，这个不局限的。就无论在哪个页面，在拍的这个过程中，它就是一个类似 Screen Studio 的效果，就它所有的典型特征都能够拿到。比方说，在最右下角有一个自己的人像，然后有跟随镜头的这么一个鼠标跟随镜头的这么一个小动效。这种东西做出来也很简单嘛。最后的效果就跟那种典型的 Screen Recorder 视频也差不多嘛。就首先 background 是自己可设置的一个背景图，然后中间一大块就是自己所选定的那个 display。那是一样的嘛？那你这个 display 被限定在浏览器里也可以啊，很多时候就是只需要讲一个网页的东西啊，你或者打开一个 local host HTML 就可以开讲了呀，是一样的道理啊。当然，这只是我的一个设想哈。
