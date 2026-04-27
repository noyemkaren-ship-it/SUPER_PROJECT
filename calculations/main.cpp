#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>
#include "crow_all.h"

int main() {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/wheel")([]() {
        std::srand(std::time(0));
        int prize = std::rand() % 100 + 1;  

        crow::json::wvalue result;
        result["prize"] = prize;
        result["message"] = "Колесо Фортуны крутанулось!";
        return result;
    });

    // Проверка здоровья
    CROW_ROUTE(app, "/health")([]() {
        return "C++ Microservice is alive!";
    });

    app.port(4444).run();
}