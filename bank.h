// bank.h - Part 1 backend interface (COP 4020 Project 1)
#ifndef BANK_H
#define BANK_H

#include <string>

// One client record. SSN and account number are strings (identifiers, not numbers).
struct Client {
    std::string client_name;
    std::string ssn;
    std::string bank_account_number;
    double balance = 0.0;
};

// ---- Free function prototypes (helpers used by Bank and testable alone) ----

// Returns s without leading/trailing whitespace.
std::string trim(const std::string& s);

// Parses "client_name,ssn,bank_account_number,balance" into a Client.
// Throws std::invalid_argument if the line is malformed.
Client parse_client_line(const std::string& line);

// Throws std::invalid_argument if the record is not valid
// (empty field, comma/newline in a field, negative or non-finite balance).
void validate_client(const Client& c);

// Manages a dynamically allocated array of Client objects.
// The backend never prints; all errors are reported with exceptions.
class Bank {
private:
    int num_clients;   // number of valid Client objects in the array
    Client* clients;   // heap-allocated array of size num_clients (nullptr if empty)

    // Index of the account, or -1 if it does not exist.
    int index_of(const std::string& account_number) const;

public:
    Bank();                                    // empty bank
    explicit Bank(const std::string& filename); // load CSV; throws std::runtime_error on failure

    // Rule of Three
    Bank(const Bank& other);                   // deep copy
    Bank& operator=(const Bank& other);        // deep copy, self-assignment safe
    ~Bank();

    // Access / search (nothing is printed)
    const Client* get_clients_info() const;    // pointer to the array (nullptr if empty)
    int get_num_clients() const;
    // Returns a pointer to the matching client, or nullptr if the account does not exist.
    const Client* find_client(const std::string& account_number) const;

    // Transactions: each returns the new balance.
    // Throw std::invalid_argument (bad amount) or std::runtime_error (unknown account,
    // insufficient funds).
    double deposit(const std::string& account_number, double amount);
    double withdraw(const std::string& account_number, double amount);

    // Throws std::invalid_argument (invalid record) or std::runtime_error (duplicate account).
    void add_new_client(const Client& c);

    // Writes every client in the same CSV format. Throws std::runtime_error on file errors.
    void save_info(const std::string& filename) const;
};

#endif // BANK_H