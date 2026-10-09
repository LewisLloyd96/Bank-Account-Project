// bank.cpp - Part 1 backend implementation (COP 4020 Project 1)
#include "bank.h"

#include <cerrno>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <vector>

// ---------------------------------------------------------------------------
// Free helpers
// ---------------------------------------------------------------------------

std::string trim(const std::string& s) {
    const char* ws = " \t\r\n";
    std::string::size_type begin = s.find_first_not_of(ws);
    if (begin == std::string::npos) return "";
    std::string::size_type end = s.find_last_not_of(ws);
    return s.substr(begin, end - begin + 1);
}

// Strict number parse: the whole string must be a finite number.
static bool parse_double(const std::string& text, double& out) {
    if (text.empty()) return false;
    char* end = nullptr;
    errno = 0;
    double value = std::strtod(text.c_str(), &end);
    if (end == text.c_str() || *end != '\0' || errno == ERANGE || !std::isfinite(value)) {
        return false;
    }
    out = value;
    return true;
}

Client parse_client_line(const std::string& line) {
    std::vector<std::string> fields;
    std::string::size_type start = 0;
    while (true) {
        std::string::size_type comma = line.find(',', start);
        if (comma == std::string::npos) {
            fields.push_back(trim(line.substr(start)));
            break;
        }
        fields.push_back(trim(line.substr(start, comma - start)));
        start = comma + 1;
    }
    if (fields.size() != 4) {
        throw std::invalid_argument("expected 4 comma-separated fields "
                                    "(client_name,ssn,bank_account_number,balance)");
    }

    Client c;
    c.client_name = fields[0];
    c.ssn = fields[1];
    c.bank_account_number = fields[2];
    if (!parse_double(fields[3], c.balance)) {
        throw std::invalid_argument("balance is not a valid number: '" + fields[3] + "'");
    }
    validate_client(c);
    return c;
}

void validate_client(const Client& c) {
    if (c.client_name.empty()) throw std::invalid_argument("client name is required");
    if (c.ssn.empty()) throw std::invalid_argument("SSN is required");
    if (c.bank_account_number.empty()) throw std::invalid_argument("account number is required");
    const std::string* fields[] = {&c.client_name, &c.ssn, &c.bank_account_number};
    for (const std::string* f : fields) {
        if (f->find_first_of(",\r\n") != std::string::npos) {
            throw std::invalid_argument("fields must not contain commas or line breaks");
        }
    }
    if (!std::isfinite(c.balance) || c.balance < 0.0) {
        throw std::invalid_argument("balance must be a finite number >= 0");
    }
}

// ---------------------------------------------------------------------------
// Construction / Rule of Three
// ---------------------------------------------------------------------------

Bank::Bank() : num_clients(0), clients(nullptr) {}

Bank::Bank(const std::string& filename) : num_clients(0), clients(nullptr) {
    std::ifstream in(filename);
    if (!in) throw std::runtime_error("Cannot open file: " + filename);

    // Parse everything into a temporary container first. If anything is wrong we
    // throw before touching our own members, so nothing leaks.
    std::vector<Client> loaded;
    std::string line;
    int line_no = 0;
    while (std::getline(in, line)) {
        ++line_no;
        std::string text = trim(line);
        if (text.empty()) continue;
        if (line_no == 1 && text.rfind("client_name,", 0) == 0) continue;  // optional header

        Client c;
        try {
            c = parse_client_line(text);
        } catch (const std::exception& e) {
            throw std::runtime_error("Line " + std::to_string(line_no) + ": " + e.what());
        }
        for (const Client& existing : loaded) {
            if (existing.bank_account_number == c.bank_account_number) {
                throw std::runtime_error("Line " + std::to_string(line_no) +
                                         ": duplicate account number " + c.bank_account_number);
            }
        }
        loaded.push_back(c);
    }
    if (in.bad()) throw std::runtime_error("Error while reading file: " + filename);

    if (!loaded.empty()) {
        clients = new Client[loaded.size()];
        num_clients = static_cast<int>(loaded.size());
        for (int i = 0; i < num_clients; ++i) clients[i] = loaded[i];
    }
}

Bank::Bank(const Bank& other) : num_clients(0), clients(nullptr) {
    if (other.num_clients > 0) {
        clients = new Client[other.num_clients];
        num_clients = other.num_clients;
        for (int i = 0; i < num_clients; ++i) clients[i] = other.clients[i];
    }
}

Bank& Bank::operator=(const Bank& other) {
    if (this == &other) return *this;  // self-assignment
    Client* fresh = nullptr;
    if (other.num_clients > 0) {
        fresh = new Client[other.num_clients];  // allocate first: if it throws, *this is unchanged
        for (int i = 0; i < other.num_clients; ++i) fresh[i] = other.clients[i];
    }
    delete[] clients;
    clients = fresh;
    num_clients = other.num_clients;
    return *this;
}

Bank::~Bank() {
    delete[] clients;
}

// ---------------------------------------------------------------------------
// Access / search
// ---------------------------------------------------------------------------

const Client* Bank::get_clients_info() const { return clients; }

int Bank::get_num_clients() const { return num_clients; }

int Bank::index_of(const std::string& account_number) const {
    for (int i = 0; i < num_clients; ++i) {
        if (clients[i].bank_account_number == account_number) return i;
    }
    return -1;
}

const Client* Bank::find_client(const std::string& account_number) const {
    int i = index_of(trim(account_number));
    return i < 0 ? nullptr : &clients[i];
}

// ---------------------------------------------------------------------------
// Transactions
// ---------------------------------------------------------------------------

double Bank::deposit(const std::string& account_number, double amount) {
    if (!std::isfinite(amount) || amount <= 0.0) {
        throw std::invalid_argument("Deposit amount must be greater than 0.");
    }
    int i = index_of(trim(account_number));
    if (i < 0) throw std::runtime_error("Account not found: " + account_number);
    clients[i].balance += amount;
    return clients[i].balance;
}

double Bank::withdraw(const std::string& account_number, double amount) {
    if (!std::isfinite(amount) || amount <= 0.0) {
        throw std::invalid_argument("Withdrawal amount must be greater than 0.");
    }
    int i = index_of(trim(account_number));
    if (i < 0) throw std::runtime_error("Account not found: " + account_number);
    if (amount > clients[i].balance) {
        std::ostringstream msg;
        msg << std::fixed << std::setprecision(2)
            << "Insufficient funds: balance is $" << clients[i].balance << ".";
        throw std::runtime_error(msg.str());
    }
    clients[i].balance -= amount;
    return clients[i].balance;
}

// ---------------------------------------------------------------------------
// Add / save
// ---------------------------------------------------------------------------

void Bank::add_new_client(const Client& c) {
    Client record = c;
    record.client_name = trim(record.client_name);
    record.ssn = trim(record.ssn);
    record.bank_account_number = trim(record.bank_account_number);
    validate_client(record);

    if (index_of(record.bank_account_number) >= 0) {
        throw std::runtime_error("Duplicate account number: " + record.bank_account_number);
    }

    // Build the bigger array first; swap it in only after everything succeeded.
    Client* bigger = new Client[num_clients + 1];
    try {
        for (int i = 0; i < num_clients; ++i) bigger[i] = clients[i];
        bigger[num_clients] = record;
    } catch (...) {
        delete[] bigger;
        throw;
    }
    delete[] clients;
    clients = bigger;
    ++num_clients;
}

void Bank::save_info(const std::string& filename) const {
    std::ofstream out(filename);
    if (!out) throw std::runtime_error("Cannot open file for writing: " + filename);

    out << std::fixed << std::setprecision(2);
    for (int i = 0; i < num_clients; ++i) {
        out << clients[i].client_name << ',' << clients[i].ssn << ','
            << clients[i].bank_account_number << ',' << clients[i].balance << '\n';
    }
    out.flush();
    if (!out) throw std::runtime_error("Error while writing file: " + filename);
}