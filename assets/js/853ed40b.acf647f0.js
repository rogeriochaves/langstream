"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[8290],{3905:(e,t,n)=>{n.d(t,{Zo:()=>p,kt:()=>h});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function s(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function m(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},o=Object.keys(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var i=a.createContext({}),l=function(e){var t=a.useContext(i),n=t;return e&&(n="function"==typeof e?e(t):s(s({},t),e)),n},p=function(e){var t=l(e.components);return a.createElement(i.Provider,{value:t},e.children)},u="mdxType",c={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},d=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,o=e.originalType,i=e.parentName,p=m(e,["components","mdxType","originalType","parentName"]),u=l(n),d=r,h=u["".concat(i,".").concat(d)]||u[d]||c[d]||o;return n?a.createElement(h,s(s({ref:t},p),{},{components:n})):a.createElement(h,s({ref:t},p))}));function h(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var o=n.length,s=new Array(o);s[0]=d;var m={};for(var i in t)hasOwnProperty.call(t,i)&&(m[i]=t[i]);m.originalType=e,m[u]="string"==typeof e?e:r,s[1]=m;for(var l=2;l<o;l++)s[l]=n[l];return a.createElement.apply(null,s)}return a.createElement.apply(null,n)}d.displayName="MDXCreateElement"},1806:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>i,contentTitle:()=>s,default:()=>c,frontMatter:()=>o,metadata:()=>m,toc:()=>l});var a=n(7462),r=(n(7294),n(3905));const o={sidebar_position:6},s="Adding Memory",m={unversionedId:"llms/memory",id:"llms/memory",title:"Adding Memory",description:"LLMs are stateless, and LangStream also strive to be as stateless as possible, which makes things easier to reason about. However, this means your Streams will have no memory by default.",source:"@site/docs/llms/memory.md",sourceDirName:"llms",slug:"/llms/memory",permalink:"/langstream/docs/llms/memory",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/llms/memory.md",tags:[],version:"current",sidebarPosition:6,frontMatter:{sidebar_position:6},sidebar:"tutorialSidebar",previous:{title:"Lite LLM (Azure, Anthropic, etc)",permalink:"/langstream/docs/llms/lite_llm"},next:{title:"Zero Temperature",permalink:"/langstream/docs/llms/zero_temperature"}},i={},l=[{value:"Simple Text Completion Memory",id:"simple-text-completion-memory",level:2},{value:"OpenAI Chat Memory",id:"openai-chat-memory",level:2}],p={toc:l},u="wrapper";function c(e){let{components:t,...n}=e;return(0,r.kt)(u,(0,a.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"adding-memory"},"Adding Memory"),(0,r.kt)("p",null,"LLMs are stateless, and LangStream also strive to be as stateless as possible, which makes things easier to reason about. However, this means your Streams will have no memory by default."),(0,r.kt)("p",null,'Following the "explicit is better than implicit" philosophy, in LangStream you manage the memory yourself, so you are in full control of what is stored to memory and where it is used and when.'),(0,r.kt)("h2",{id:"simple-text-completion-memory"},"Simple Text Completion Memory"),(0,r.kt)("p",null,"The memory can be as simple as a variable, like this ",(0,r.kt)("a",{parentName:"p",href:"gpt4all"},"GPT4All")," chatbot with memory:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from langstream import Stream, join_final_output\nfrom langstream.contrib import GPT4AllStream\nfrom textwrap import dedent\n\nmemory = ""\n\ndef save_to_memory(str: str) -> str:\n    global memory\n    memory += str\n    return str\n\nmagical_numbers_bot: Stream[str, str] = GPT4AllStream[str, str](\n    "MagicalNumbersStream",\n    lambda user_message:\n        memory\n        + save_to_memory(f"""\\n\n            ### User: {user_message}\n\n            ### Response:"""\n        ),\n    model="orca-mini-3b.ggmlv3.q4_0.bin",\n    temperature=0,\n).map(save_to_memory)\n\nawait join_final_output(magical_numbers_bot("Did you know that komodo dragons can eat people?"))\n#=> \'Yes, I do know that fact. They are known to be one of the largest and deadliest lizards in the world.\'\n\nawait join_final_output(magical_numbers_bot("Would you like to be one?"))\n#=> \' As an AI, I am not capable of feeling emotions or desires to eat people.\'\n')),(0,r.kt)("p",null,"In the second question, ",(0,r.kt)("inlineCode",{parentName:"p"},'"Would you like to be one?"'),", there is no mention of komodo dragons or eating people, still, the LLM was able to answer it considering previous context, this proves that memory is working properly."),(0,r.kt)("p",null,"The way this memory implementation works is very simple, we have a string to hold the memory, which we use it when creating the prompt (on ",(0,r.kt)("inlineCode",{parentName:"p"},"memory + ..."),")."),(0,r.kt)("p",null,"Then, we have a ",(0,r.kt)("inlineCode",{parentName:"p"},"save_to_memory")," function, which just takes any string, appends it to the ",(0,r.kt)("inlineCode",{parentName:"p"},"memory")," variable, and return the same string back, we use it in two places: when creating the prompt, to be able to save the user input to memory, and then on the ",(0,r.kt)("inlineCode",{parentName:"p"},"map(save_to_memory)")," function, which appends each generated token to memory as they come."),(0,r.kt)("p",null,"Try adding some ",(0,r.kt)("inlineCode",{parentName:"p"},"print(memory)")," statements before and after each stream call to see how memory is changing."),(0,r.kt)("h2",{id:"openai-chat-memory"},"OpenAI Chat Memory"),(0,r.kt)("p",null,"Adding memory to OpenAI Chat is a bit more tricky, because it takes a list of ",(0,r.kt)("a",{parentName:"p",href:"pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatMessage"},(0,r.kt)("inlineCode",{parentName:"a"},"OpenAIChatMessage")),"s for the prompt, and generates ",(0,r.kt)("a",{parentName:"p",href:"pathname:///reference/langstream/contrib/index.html#langstream.contrib.OpenAIChatMessage"},(0,r.kt)("inlineCode",{parentName:"a"},"OpenAIChatDelta")),"s as output."),(0,r.kt)("p",null,"This means that we cannot use a simple string as memory, but we can use a simple list. Also now we need a function to update the last message on the memory with the incoming delta for each update, like this:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from langstream import Stream, join_final_output\nfrom langstream.contrib import OpenAIChatMessage, OpenAIChatDelta, OpenAIChatStream\nfrom typing import List\n\n\nmemory: List[OpenAIChatMessage] = []\n\n\ndef save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:\n    memory.append(message)\n    return message\n\n\ndef update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:\n    if memory[-1].role != delta.role and delta.role is not None:\n        memory.append(OpenAIChatMessage(role=delta.role, content=delta.content))\n    else:\n        memory[-1].content += delta.content\n    return delta\n\n\nstream: Stream[str, str] = (\n    OpenAIChatStream[str, OpenAIChatDelta](\n        "EmojiChatStream",\n        lambda user_message: [\n            *memory,\n            save_message_to_memory(\n                OpenAIChatMessage(\n                    role="user", content=f"{user_message}. Reply in emojis"\n                )\n            ),\n        ],\n        model="gpt-3.5-turbo",\n        temperature=0,\n    )\n    .map(update_delta_on_memory)\n    .map(lambda delta: delta.content)\n)\n\nawait join_final_output(stream("Hey there, my name is \ud83e\udde8 how is it going?"))\n#=> \'\ud83d\udc4b\ud83e\udde8\ud83d\ude0a\'\n\nawait join_final_output(stream("What is my name?"))\n#=> \'\ud83e\udd14\u2753\ud83e\udde8\'\n')),(0,r.kt)("p",null,"You can see that the LLM remembers your name, which is \ud83e\udde8, a very common name nowadays."),(0,r.kt)("p",null,"In this example, we do a similar thing that we did on the first one, except that instead of concatenating the memory into the prompt string, we are expanding it into the prompt list with ",(0,r.kt)("inlineCode",{parentName:"p"},"*memory"),". Also, we cannot use the same function on the ",(0,r.kt)("inlineCode",{parentName:"p"},"map")," call, because we don't have full messages back, but deltas, which we need to use to update the last message on the memory, the function ",(0,r.kt)("inlineCode",{parentName:"p"},"update_delta_on_memory")," takes care of that for us."),(0,r.kt)("p",null,"I hope this guide now made it more clear how can you have memory on your Streams. In future releases, LangStream might release a more standard way of dealing with memory, but this is not the case yet, please join us in the discussion on how an official memory module should look like if you have ideas!"))}c.isMDXComponent=!0}}]);