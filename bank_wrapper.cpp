// bank_wrapper.cpp
// C-compatible wrapper around the Part 1 Bank class.
// Every exported function catches all C++ exceptions and reports them to
// Python through a status code (1 = success, 0 = failure) plus an error buffer.
// No banking rules live here: the wrapper only converts types and errors.

#include <cstring>
#include <exception>
#include <memory>
#include <stdexcept>
#include <string>

#include "bank.h"

#if defined(_WIN32)
#define BANK_API __declspec(dllexport)
#else
#define BANK_API __attribute__((visibility("default")))
#endif

namespace {

void copy_text(char* buffer, int size, const std::string& text) {
    if (buffer && size > 0) {
        std::strncpy(buffer, text.c_str(), static_cast<size_t>(size) - 1);
        buffer[size - 1] = '\0';
    }
}

std::string safe_str(const char* s) { return s ? std::string(s) : std::string(); }

}  // namespace

extern "C" {

// Creates a Bank. A non-empty filename is loaded by the Bank constructor.
// Returns nullptr on failure and writes a message into error.
BANK_API Bank* bank_create(const char* filename, char* error, int error_size) {
    try {
        std::string name = safe_str(filename);
        std::unique_ptr<Bank> bank(name.empty() ? new Bank() : new Bank(name));
        return bank.release();
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error while creating the bank.");
    }
    return nullptr;
}

BANK_API void bank_destroy(Bank* bank) {
    delete bank;
}

BANK_API int bank_save_file(Bank* bank, const char* filename, char* error, int error_size) {
    if (!bank) {
        copy_text(error, error_size, "Bank is not initialized.");
        return 0;
    }
    try {
        bank->save_info(safe_str(filename));
        return 1;
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error while saving.");
    }
    return 0;
}

BANK_API int bank_find_client(Bank* bank, const char* account_number,
                              char* name_out, int name_size,
                              char* ssn_out, int ssn_size,
                              double* balance_out,
                              char* error, int error_size) {
    if (!bank) {
        copy_text(error, error_size, "Bank is not initialized.");
        return 0;
    }
    try {
        std::string acct = safe_str(account_number);
        const Client* c = bank->find_client(acct);
        if (!c) throw std::runtime_error("Account not found: " + acct);
        copy_text(name_out, name_size, c->client_name);
        copy_text(ssn_out, ssn_size, c->ssn);
        if (balance_out) *balance_out = c->balance;
        return 1;
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error while searching for the client.");
    }
    return 0;
}

BANK_API int bank_deposit(Bank* bank, const char* account_number, double amount,
                          double* new_balance, char* error, int error_size) {
    if (!bank) {
        copy_text(error, error_size, "Bank is not initialized.");
        return 0;
    }
    try {
        double updated = bank->deposit(safe_str(account_number), amount);
        if (new_balance) *new_balance = updated;
        return 1;
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error during deposit.");
    }
    return 0;
}

BANK_API int bank_withdraw(Bank* bank, const char* account_number, double amount,
                           double* new_balance, char* error, int error_size) {
    if (!bank) {
        copy_text(error, error_size, "Bank is not initialized.");
        return 0;
    }
    try {
        double updated = bank->withdraw(safe_str(account_number), amount);
        if (new_balance) *new_balance = updated;
        return 1;
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error during withdrawal.");
    }
    return 0;
}

BANK_API int bank_add_client(Bank* bank, const char* account_number, const char* name,
                             const char* ssn, double initial_balance,
                             char* error, int error_size) {
    if (!bank) {
        copy_text(error, error_size, "Bank is not initialized.");
        return 0;
    }
    try {
        Client c;
        c.client_name = safe_str(name);
        c.ssn = safe_str(ssn);
        c.bank_account_number = safe_str(account_number);
        c.balance = initial_balance;
        bank->add_new_client(c);
        return 1;
    } catch (const std::exception& e) {
        copy_text(error, error_size, e.what());
    } catch (...) {
        copy_text(error, error_size, "Unknown error while adding the client.");
    }
    return 0;
}

}  // extern "C"