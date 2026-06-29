async function main() {
  const FarmChain = await ethers.getContractFactory("FarmChain");
  const farmchain = await FarmChain.deploy();
  await farmchain.waitForDeployment();
  const address = await farmchain.getAddress();
  console.log("CONTRACT_ADDRESS=" + address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
