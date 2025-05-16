def form_errors(e):
    msg=""
    for i in e:
        if i.errors:
            msg+=i.errors
    
    for k in e.non_field_errors():
        msg +=str(k)
    
    return msg