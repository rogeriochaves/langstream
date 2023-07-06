"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[9671],{3905:(e,t,n)=>{n.d(t,{Zo:()=>c,kt:()=>h});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},i=Object.keys(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var s=a.createContext({}),p=function(e){var t=a.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},c=function(e){var t=p(e.components);return a.createElement(s.Provider,{value:t},e.children)},u="mdxType",m={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},d=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,i=e.originalType,s=e.parentName,c=l(e,["components","mdxType","originalType","parentName"]),u=p(n),d=r,h=u["".concat(s,".").concat(d)]||u[d]||m[d]||i;return n?a.createElement(h,o(o({ref:t},c),{},{components:n})):a.createElement(h,o({ref:t},c))}));function h(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=n.length,o=new Array(i);o[0]=d;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l[u]="string"==typeof e?e:r,o[1]=l;for(var p=2;p<i;p++)o[p]=n[p];return a.createElement.apply(null,o)}return a.createElement.apply(null,n)}d.displayName="MDXCreateElement"},9881:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>s,contentTitle:()=>o,default:()=>m,frontMatter:()=>i,metadata:()=>l,toc:()=>p});var a=n(7462),r=(n(7294),n(3905));const i={sidebar_position:1},o="Getting Started",l={unversionedId:"intro",id:"intro",title:"Getting Started",description:"LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable.",source:"@site/docs/intro.md",sourceDirName:".",slug:"/intro",permalink:"/litechain/docs/intro",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/intro.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1},sidebar:"tutorialSidebar",next:{title:"Chain Basics",permalink:"/litechain/docs/chain-basics/"}},s={},p=[{value:"Your First Chain",id:"your-first-chain",level:2},{value:"Next Steps",id:"next-steps",level:2}],c={toc:p},u="wrapper";function m(e){let{components:t,...n}=e;return(0,r.kt)(u,(0,a.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"getting-started"},"Getting Started"),(0,r.kt)("p",null,"LiteChain is a lighter alternative to LangChain for building LLMs application, instead of having a massive amount of features and classes, LiteChain focuses on having a single small core, that is easy to learn, easy to adapt, well documented, fully typed and truly composable."),(0,r.kt)("p",null,"You can install it with pip:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"pip install litechain\n")),(0,r.kt)("h2",{id:"your-first-chain"},"Your First Chain"),(0,r.kt)("p",null,"To run this example, first you will need to get an ",(0,r.kt)("a",{parentName:"p",href:"https://platform.openai.com"},"API key from OpenAI"),", then export it with:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"export OPENAI_API_KEY=<your key here>\n")),(0,r.kt)("p",null,"(if you really cannot get access to the API, you can try ",(0,r.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/contrib/index.html#litechain.contrib.GPT4AllChain"},"GPT4All")," instead, it's completely free and runs locally)"),(0,r.kt)("p",null,"Now create a new file ",(0,r.kt)("inlineCode",{parentName:"p"},"main.py")," and paste this example:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from litechain.contrib import OpenAIChatChain, OpenAIChatMessage, OpenAIChatDelta\nimport asyncio\n\n# Creating a GPT-3.5 EmojiChain\nemoji_chain = OpenAIChatChain[str, OpenAIChatDelta](\n    "EmojiChain",\n    lambda user_message: [\n        OpenAIChatMessage(\n            role="user", content=f"{user_message}. Reply in emojis"\n        )\n    ],\n    model="gpt-3.5-turbo",\n    temperature=0,\n)\n\nasync def main():\n    while True:\n        print("> ", end="")\n        async for output in emoji_chain(input()):\n            print(output.data.content, end="")\n        print("")\n\nasyncio.run(main())\n')),(0,r.kt)("p",null,"Now run it with"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre"},"python main.py\n")),(0,r.kt)("p",null,"This will create a basic chat on the terminal, and for any questions you ask the bot, it will answer in emojis. If you terminal does not support emojis, try changing the prompt, asking it to reply in ASCII art for example."),(0,r.kt)("h2",{id:"next-steps"},"Next Steps"),(0,r.kt)("p",null,"Continue on reading to learn the Chain basics, we will then build up on more complex examples, can't wait!"))}m.isMDXComponent=!0}}]);