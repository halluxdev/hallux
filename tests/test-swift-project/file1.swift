//
//
//

protocol RefreshContractMeController {
    func refreshContractMe(completion: @escaping (Result<Void, Error>) -> Void)
}

extension RefreshContractMeController {
    private func handleSonarQubeViolation() {
        print("I'm a violation!")
    }
}
