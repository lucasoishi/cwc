import helpers


def main():
    balance = helpers.get_balance_conversions()
    helpers.save_to_file(balance)


if __name__ == '__main__':
    main()
