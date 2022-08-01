date = "2022-08-30T00:46:56+02:00"
expiredate = Date.parse(date)
console.log(expiredate)
console.log(Date.now())
if (expiredate < Date.now()) {
    console.log("Date is not valid")
}