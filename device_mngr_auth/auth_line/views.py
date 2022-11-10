@extend_schema(responses={200: {}}, methods=['POST'], )
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def callback(request):
    # send_json = json.loads(request.body)
    # reply_token = send_json['events'][0]['replyToken']
    # user_id = send_json['events'][0]['source']['userId']
    # # line_bot_api.reply_message(reply_token, TextSendMessage(text='Hello World!'))
    try:
        profile = line_bot_api.get_profile(user_id='U0fb11ef46062a25ed4e78cd9665ecef5')
    except LineBotApiError as e:
        return Response(e.message)

    print(profile.display_name)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.status_message)
    return Response("hello")