def process(trains, events, car):
    res = None
    for event in events:
        if event['type'] == 'walk':
            a = walk(trains, event)
            if a == -1:
                res = -1
        elif event['type'] == 'switch':
            b = switch(trains, event)
            if b == -1:
                res = -1
        else:
            res = -1
    return res or result_function(trains, car)


# walk
# поиск пассажира в вагоне (возвращает номер вагона)
def find_person(trains, event):
    car_number = -1
    train_number = -1
    for train_index in range(len(trains)):
        for current_index in range(len(trains[train_index]['cars'])):
            if event['passenger'] in trains[train_index]['cars'][current_index]['people']:
                car_number = current_index
                train_number = train_index
    return car_number, train_number


# поиск заданного вагона и поезда
def find_car(trains, car):
    result_car_index = -1
    result_train_index = -1
    for train_index in range(len(trains)):
        for current_index in range(len(trains[train_index]['cars'])):
            if car in trains[train_index]['cars'][current_index]['name']:
                result_car_index = current_index
                result_train_index = train_index
    return result_car_index, result_train_index


# подсчет вагонов в поезде
def walk(trains, event):
    error = None
    car_number, train_number = find_person(trains, event)
    if car_number == -1 or train_number == -1:
        error = -1
    if 0 < car_number + event['distance'] + 1 <= len(trains[train_number]['cars']):
        trains[train_number]['cars'][car_number + event['distance']]['people'].append(event['passenger'])
        trains[train_number]['cars'][car_number]['people'].remove(event['passenger'])
    else:
        error = - 1
    return error


# подсчет людей в интересующем вагоне
def result_function(trains, car):
    result_car_index, result_train_index = find_car(trains, car)
    if result_car_index == -1 or result_train_index == -1:
        message = - 1
    else:
        message = len(trains[result_train_index]['cars'][result_car_index]['people'])
    return message


# switch
# есть ли указанные поезда
def find_trains_to_switch(trains, event):
    train_from_index = -1
    train_to_index = -1
    for current_train_index in range(len(trains)):
        if event['train_from'] in trains[current_train_index]['name']:
            train_from_index = current_train_index
        if event['train_to'] in trains[current_train_index]['name']:
            train_to_index = current_train_index
    return train_from_index, train_to_index


# есть ли нужное количество вагонов в train_from, если да, то меняем
def switch(trains, event):
    train_from_index, train_to_index = find_trains_to_switch(trains, event)
    error_1 = None
    if train_from_index == -1 or train_to_index == -1:
        error_1 = -1
    if 0 != event['cars'] <= len(trains[train_from_index]['cars']):
        trains[train_to_index]['cars'].extend(trains[train_from_index]['cars'][-event['cars']:])
        del trains[train_from_index]['cars'][-event['cars']:]
    elif event['cars'] == 0:
        error_1 = None
    else:
        error_1 = -1
    return error_1
