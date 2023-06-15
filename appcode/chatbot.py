import openai
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from rest_framework.decorators import api_view
from django.http import JsonResponse
from jetsetpack.settings import API_KEY



@api_view(['GET'])
def chat_bot(request):
    if request.method == 'GET':
        try:
            human_input = request.data.get('human_input')

            template = """
            You are a Grid Dynamics chatbot having a conversation with a human.
            {chat_history}
            Human: {human_input}
            Chatbot:
            """

            prompt = PromptTemplate(
                input_variables=["human_input","chat_history"], 
                template=template
            )
            memory = ConversationBufferMemory(memory_key="chat_history")
            llm_chain = LLMChain(
                llm=OpenAI(temperature=0.2,model="text-davinci-003" ,openai_api_key=API_KEY), 
                prompt=prompt, 
                verbose=True, 
                memory=memory,
            )
            response = llm_chain.predict(human_input="human_input")
            print(response)

            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({"message": str(e)})
    else:
        return JsonResponse({"message":"Request method is not supported."})
