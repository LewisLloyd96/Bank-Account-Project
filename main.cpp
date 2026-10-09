// main.cpp - console test driver for the Part 1 backend (not the GUI)
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

#include "bank.h"

static void print_client(const Client& c) {
    std::cout << "  " << c.client_name << " | " << c.ssn << " | "
              << c.bank_account_number << " | $" << c.balance << "\n";
}

static void print_balance(const Bank& bank, const std::string& acct) {
    const Client* c = bank.find_client(acct);
    if (c) std::cout << "  Balance of " << acct << ": $" << c->balance << "\n";
}

// Runs an action that is EXPECTED to throw and reports what happened.
template <typename Fn>
static void expect_error(const std::string& label, Fn action) {
    try {
        action();
        std::cout << "  [FAIL] " << label << ": no error was raised\n";
    } catch (const std::exception& e) {
        std::cout << "  [PASS] " << label << " -> " << e.what() << "\n";
    }
}

int main() {
    std::cout << std::fixed << std::setprecision(2);
    try {
        std::cout << "== 1. Load file ==\n";
        Bank bank("clients.csv");
        std::cout << "  Loaded " << bank.get_num_clients() << " clients\n";
        for (int i = 0; i < bank.get_num_clients(); ++i) print_client(bank.get_clients_info()[i]);

        std::cout << "\n== 2. Search ==\n";
        const Client* found = bank.find_client("0001234567");
        if (found) { std::cout << "  Found existing account:\n"; print_client(*found); }
        else std::cout << "  [FAIL] existing account not found\n";
        if (!bank.find_client("9999999999")) std::cout << "  [PASS] missing account handled (nullptr)\n";
        else std::cout << "  [FAIL] missing account was found\n";

        std::cout << "\n== 3. Valid deposit / withdrawal ==\n";
        std::cout << "  Deposit 100.00 -> new balance $" << bank.deposit("0001234567", 100.00) << "\n";
        std::cout << "  Withdraw 50.25 -> new balance $" << bank.withdraw("0001234567", 50.25) << "\n";

        std::cout << "\n== 4. Invalid transactions ==\n";
        expect_error("deposit of -5", [&] { bank.deposit("0001234567", -5.0); });
        expect_error("deposit of 0", [&] { bank.deposit("0001234567", 0.0); });
        expect_error("withdrawal of 0", [&] { bank.withdraw("0001234567", 0.0); });
        expect_error("withdrawal of -1", [&] { bank.withdraw("0001234567", -1.0); });
        expect_error("insufficient funds", [&] { bank.withdraw("0001234567", 1000000.0); });
        expect_error("deposit to unknown account", [&] { bank.deposit("9999999999", 10.0); });
        print_balance(bank, "0001234567");

        std::cout << "\n== 5. Add client / duplicate ==\n";
        int before = bank.get_num_clients();
        Client fresh;
        fresh.client_name = "Test Person";
        fresh.ssn = "000-11-2222";
        fresh.bank_account_number = "0000000001";
        fresh.balance = 25.00;
        bank.add_new_client(fresh);
        std::cout << "  Clients: " << before << " -> " << bank.get_num_clients() << "\n";
        bool preserved = true;
        for (int i = 0; i < before; ++i) {
            if (bank.get_clients_info()[i].bank_account_number.empty()) preserved = false;
        }
        std::cout << "  " << (preserved && bank.find_client("0001234567") ? "[PASS]" : "[FAIL]")
                  << " existing clients preserved\n";
        expect_error("duplicate account number", [&] { bank.add_new_client(fresh); });
        Client bad = fresh;
        bad.bank_account_number = "0000000002";
        bad.client_name = "";
        expect_error("empty client name", [&] { bank.add_new_client(bad); });

        std::cout << "\n== 6. Save to a new file ==\n";
        bank.save_info("clients_saved.csv");
        Bank reloaded("clients_saved.csv");
        std::cout << "  Saved and reloaded: " << reloaded.get_num_clients() << " clients "
                  << (reloaded.get_num_clients() == bank.get_num_clients() ? "[PASS]" : "[FAIL]")
                  << "\n";
        expect_error("load missing file", [] { Bank b("no_such_file.csv"); });
        expect_error("save to bad path", [&] { bank.save_info("/no/such/dir/out.csv"); });

        std::cout << "\n== 7. Deep copy ==\n";
        Bank copy(bank);                       // copy constructor
        copy.deposit("0001234567", 500.00);
        copy.add_new_client(Client{"Copy Only", "111-22-3333", "0000000099", 1.0});
        std::cout << "  Original clients: " << bank.get_num_clients()
                  << ", copy clients: " << copy.get_num_clients() << "\n";
        std::cout << "  Original "; print_balance(bank, "0001234567");
        std::cout << "  Copy     "; print_balance(copy, "0001234567");

        Bank assigned;
        assigned = bank;                       // copy assignment
        assigned.withdraw("0001234567", 10.00);
        assigned = assigned;                   // self-assignment must be safe
        std::cout << "  Assigned "; print_balance(assigned, "0001234567");
        std::cout << "  Original "; print_balance(bank, "0001234567");
        std::cout << "\nDone.\n";
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
