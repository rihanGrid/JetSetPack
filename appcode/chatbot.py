import openai
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.http import JsonResponse



@api_view(['POST'])
def chat_bot(request):
    if request.method == 'POST':
        try:
            human_input = request.data.get('human_input')
            template = """You are a chatbot having a conversation with a human.
            {chat_history}
            Human: {human_input}
            Chatbot:"""

            prompt = PromptTemplate(
                input_variables=["chat_history", "human_input"], 
                template=template
            )
            memory = ConversationBufferMemory(memory_key="chat_history")

            llm_chain = LLMChain(
                llm=OpenAI(openai_api_key="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"), 
                prompt=prompt, 
                verbose=True, 
                memory=memory,
            )

            response = llm_chain.predict(human_input=human_input)

            # memory.save_context({
            #     "human_input": human_input,
            #     "response": response
            # })

            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({"message": str(e)})
    else:
        return JsonResponse({"message":"Request method is not supported."})
