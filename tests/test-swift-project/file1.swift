//
//
//

protocol TestController {
    func refreshContractMe(completion: @escaping (Result<Void, Error>) -> Void)
}

extension TestController {
    private func handleSonarQubeViolation() {
        print("I'm a violation!")
    }
}
